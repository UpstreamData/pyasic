#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import ipaddress
import json
import logging
from typing import List, Union, Tuple, Optional
from collections import namedtuple

import asyncssh
import httpx
import toml

from pyasic.API.bosminer import BOSMinerAPI
from pyasic.config import MinerConfig
from pyasic.data import HashBoard, MinerData
from pyasic.data.error_codes import BraiinsOSError, MinerErrorData
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner
from pyasic.settings import PyasicSettings


class BOSMiner(BaseMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = BOSMinerAPI(ip, api_ver)
        self.api_type = "BOSMiner"
        self.api_ver = api_ver
        self.uname = "root"
        self.pwd = "admin"
        self.config = None

    async def send_ssh_command(self, cmd: str) -> Union[str, None]:
        result = None

        try:
            conn = await self._get_ssh_connection()
        except asyncssh.Error:
            return None

        # open an ssh connection
        async with conn:
            # 3 retries
            for i in range(3):
                try:
                    # run the command and get the result
                    result = await conn.run(cmd)
                    result = result.stdout

                except Exception as e:
                    # if the command fails, log it
                    logging.warning(f"{self} command {cmd} error: {e}")

                    # on the 3rd retry, return None
                    if i == 3:
                        return
                    continue
        # return the result, either command output or None
        return result

    async def send_graphql_query(self, query) -> Union[dict, None]:
        # FW version must be equal to or greater than 21.09 to use this
        if self.fw_ver:
            if not (
                (
                    int(self.fw_ver.split(".")[0]) == 21
                    and int(self.fw_ver.split(".")[1]) >= 9
                )
                or int(self.fw_ver.split(".")[0]) > 21
            ):
                logging.info(f"FW version {self.fw_ver} is too low to use graphql.")
                return None

        url = f"http://{self.ip}/graphql"
        try:
            async with httpx.AsyncClient() as client:
                _auth = await client.post(
                    url,
                    json={
                        "query": 'mutation{auth{login(username:"'
                        + self.uname
                        + '", password:"'
                        + self.pwd
                        + '"){__typename}}}'
                    },
                )
                d = await client.post(url, json={"query": query})
            if d.status_code == 200:
                return d.json()
        except (httpx.ReadError, httpx.ReadTimeout):
            return None
        return None

    async def fault_light_on(self) -> bool:
        """Sends command to turn on fault light on the miner."""
        logging.debug(f"{self}: Sending fault_light on command.")
        _ret = await self.send_ssh_command("miner fault_light on")
        logging.debug(f"{self}: fault_light on command completed.")
        if isinstance(_ret, str):
            self.light = True
            return self.light
        return False

    async def fault_light_off(self) -> bool:
        """Sends command to turn off fault light on the miner."""
        logging.debug(f"{self}: Sending fault_light off command.")
        self.light = False
        _ret = await self.send_ssh_command("miner fault_light off")
        logging.debug(f"{self}: fault_light off command completed.")
        if isinstance(_ret, str):
            self.light = False
            return True
        return False

    async def restart_backend(self) -> bool:
        """Restart bosminer hashing process.  Wraps [`restart_bosminer`][pyasic.miners._backends.bosminer.BOSMiner.restart_bosminer] to standardize."""
        return await self.restart_bosminer()

    async def restart_bosminer(self) -> bool:
        """Restart bosminer hashing process."""
        logging.debug(f"{self}: Sending bosminer restart command.")
        _ret = await self.send_ssh_command("/etc/init.d/bosminer restart")
        logging.debug(f"{self}: bosminer restart command completed.")
        if isinstance(_ret, str):
            return True
        return False

    async def stop_mining(self) -> bool:
        data = await self.api.pause()
        if data.get("PAUSE"):
            if data["PAUSE"][0]:
                return True
        return False

    async def resume_mining(self) -> bool:
        data = await self.api.resume()
        if data.get("RESUME"):
            if data["RESUME"][0]:
                return True
        return False

    async def reboot(self) -> bool:
        """Reboots power to the physical miner."""
        logging.debug(f"{self}: Sending reboot command.")
        _ret = await self.send_ssh_command("/sbin/reboot")
        logging.debug(f"{self}: Reboot command completed.")
        if isinstance(_ret, str):
            return True
        return False

    async def get_config(self) -> MinerConfig:
        """Gets the config for the miner and sets it as `self.config`.

        Returns:
            The config from `self.config`.
        """
        logging.debug(f"{self}: Getting config.")
        async with (await self._get_ssh_connection()) as conn:
            logging.debug(f"{self}: Opening SFTP connection.")
            async with conn.start_sftp_client() as sftp:
                logging.debug(f"{self}: Reading config file.")
                async with sftp.open("/etc/bosminer.toml") as file:
                    toml_data = toml.loads(await file.read())
        logging.debug(f"{self}: Converting config file.")
        cfg = MinerConfig().from_raw(toml_data)
        self.config = cfg
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        """Configures miner with yaml config."""
        logging.debug(f"{self}: Sending config.")
        toml_conf = config.as_bos(
            model=self.model.replace(" (BOS)", ""), user_suffix=user_suffix
        )
        async with (await self._get_ssh_connection()) as conn:
            await conn.run("/etc/init.d/bosminer stop")
            logging.debug(f"{self}: Opening SFTP connection.")
            async with conn.start_sftp_client() as sftp:
                logging.debug(f"{self}: Opening config file.")
                async with sftp.open("/etc/bosminer.toml", "w+") as file:
                    await file.write(toml_conf)
            logging.debug(f"{self}: Restarting BOSMiner")
            await conn.run("/etc/init.d/bosminer start")

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            cfg = await self.get_config()
            cfg.autotuning_wattage = wattage
            await self.send_config(cfg)
        except Exception as e:
            logging.warning(f"{self} set_power_limit: {e}")
            return False
        else:
            return True

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(self) -> Optional[str]:
        try:
            result = await self.send_ssh_command("cat /sys/class/net/eth0/address")
            return result.upper().strip()
        except asyncssh.Error:
            pass

    async def get_model(self) -> Optional[str]:
        # check if model is cached
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model} (BOS)")
            return self.model + " (BOS)"

        # get devdetails data
        try:
            version_data = await self.api.devdetails()
        except APIError as e:
            version_data = None
            if e.message == "Not ready":
                cfg = json.loads(await self.send_ssh_command("bosminer config --data"))
                model = cfg.get("data").get("format").get("model")
                if model:
                    model = model.replace("Antminer ", "")
                    self.model = model
                    return self.model + " (BOS)"

        # if we get data back, parse it for model
        if version_data:
            if not version_data["DEVDETAILS"] == []:
                # handle Antminer BOSMiner as a base
                self.model = version_data["DEVDETAILS"][0]["Model"].replace(
                    "Antminer ", ""
                )
                logging.debug(f"Found model for {self.ip}: {self.model} (BOS)")
                return self.model + " (BOS)"

        # if we don't get devdetails, log a failed attempt
        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def get_version(
        self, api_version: dict = None, graphql_version: dict = None
    ) -> Tuple[Optional[str], Optional[str]]:
        # check if version is cached
        miner_version = namedtuple("MinerVersion", "api_ver fw_ver")
        if self.fw_ver and self.api_ver:
            logging.debug(f"Found version for {self.ip}: {self.fw_ver}")
            return miner_version(self.api_ver, self.fw_ver)

        if not graphql_version:
            graphql_version = await self.send_graphql_query(
                "{bos{info{version{full}}}}"
            )

        if not api_version:
            api_version = await self.api.version()
        fw_ver = None

        if graphql_version:
            try:
                fw_ver = graphql_version["bos"]["info"]["version"]["full"]
            except KeyError:
                pass

        if not fw_ver:
            # try version data file
            fw_ver = await self.send_ssh_command("cat /etc/bos_version")

        # if we get the version data, parse it
        if fw_ver:
            logging.debug(f"Found version for {self.ip}: {self.fw_ver}")
            self.fw_ver = fw_ver.split("-")[5]

        # Now get the API version
        if api_version:
            try:
                api_ver = api_version["VERSION"][0]["API"]
            except (KeyError, IndexError):
                api_ver = None
            self.api_ver = api_ver
            self.api.api_ver = self.api_ver

        return miner_version(self.api_ver, self.fw_ver)

    async def get_hostname(self, graphql_hostname: dict = None) -> Union[str, None]:
        if self.hostname:
            return self.hostname

        if not graphql_hostname:
            graphql_hostname = await self.send_graphql_query("{bos {hostname}}")

        if graphql_hostname:
            self.hostname = graphql_hostname["bos"]["hostname"]
            return self.hostname

        try:
            async with (await self._get_ssh_connection()) as conn:
                if conn is not None:
                    data = await conn.run("cat /proc/sys/kernel/hostname")
                    host = data.stdout.strip()
                    logging.debug(f"Found hostname for {self.ip}: {host}")
                    self.hostname = host
                else:
                    logging.warning(f"Failed to get hostname for miner: {self}")
        except Exception as e:
            logging.warning(f"Failed to get hostname for miner: {self}, {e}")
        return self.hostname

    async def get_hashrate(
        self, api_summary: dict = None, graphql_hashrate: dict = None
    ) -> Optional[float]:

        # get hr from graphql
        if not graphql_hashrate:
            graphql_hashrate = await self.send_graphql_query(
                "{bosminer{info{workSolver{realHashrate{mhs1M}}}}}"
            )

        if graphql_hashrate:
            try:
                return round(
                    float(
                        graphql_hashrate["bosminer"]["info"]["workSolver"][
                            "realHashrate"
                        ]["mhs1M"]
                        / 1000000
                    ),
                    2,
                )
            except (KeyError, IndexError, ValueError):
                pass

        # get hr from API
        if not api_summary:
            api_summary = await self.api.summary()

        if api_summary:
            try:
                return round(float(api_summary["SUMMARY"][0]["MHS 1m"] / 1000000), 2)
            except (KeyError, IndexError, ValueError, TypeError):
                pass

    async def get_hashboards(
        self,
        api_temps: dict = None,
        api_devdetails: dict = None,
        api_devs: dict = None,
        graphql_boards: dict = None,
    ):
        hashboards = [
            HashBoard(slot=i, expected_chips=self.nominal_chips)
            for i in range(self.ideal_hashboards)
        ]

        if not graphql_boards and not (api_devs or api_temps or api_devdetails):
            graphql_boards = await self.send_graphql_query(
                "{bosminer{info{workSolver{childSolvers{name, realHashrate {mhs1M}, hwDetails {chips}, temperatures {degreesC}}}}}}"
            )

        if graphql_boards:
            try:
                boards = graphql_boards["bosminer"]["info"]["workSolver"][
                    "childSolvers"
                ]
            except (KeyError, IndexError):
                boards = None

            if boards:
                offset = 6 if int(boards[0]["name"]) in [6, 7, 8] else 0
                for hb in boards:
                    _id = int(hb["name"]) - offset
                    board = hashboards[_id]

                    board.hashrate = round(hb["realHashrate"]["mhs1M"] / 1000000, 2)
                    temps = hb["temperatures"]
                    try:
                        if len(temps) > 0:
                            board.temp = round(hb["temperatures"][0]["degreesC"])
                        if len(temps) > 1:
                            board.chip_temp = round(hb["temperatures"][1]["degreesC"])
                    except (TypeError, KeyError, ValueError, IndexError):
                        pass
                    details = hb.get("hwDetails")
                    if details:
                        if chips := details["chips"]:
                            board.chips = chips
                    board.missing = False

                return hashboards

        cmds = []
        if not api_temps:
            cmds.append("temps")
        if not api_devdetails:
            cmds.append("devdetails")
        if not api_devs:
            cmds.append("devs")
        if len(cmds) > 0:
            print(cmds)
            d = await self.api.multicommand(*cmds)
            try:
                api_temps = d["temps"][0]
            except (KeyError, IndexError):
                api_temps = None
            try:
                api_devdetails = d["devdetails"][0]
            except (KeyError, IndexError):
                api_devdetails = None
            try:
                api_devs = d["devs"][0]
            except (KeyError, IndexError):
                api_devs = None

        if api_temps:
            try:
                offset = 6 if api_temps["TEMPS"][0]["ID"] in [6, 7, 8] else 0

                for board in api_temps["TEMPS"]:
                    _id = board["ID"] - offset
                    chip_temp = round(board["Chip"])
                    board_temp = round(board["Board"])
                    hashboards[_id].chip_temp = chip_temp
                    hashboards[_id].temp = board_temp
            except (IndexError, KeyError, ValueError, TypeError):
                pass

        if api_devdetails:
            try:
                offset = 6 if api_devdetails["DEVDETAILS"][0]["ID"] in [6, 7, 8] else 0

                for board in api_devdetails["DEVDETAILS"]:
                    _id = board["ID"] - offset
                    chips = board["Chips"]
                    hashboards[_id].chips = chips
                    hashboards[_id].missing = False
            except (IndexError, KeyError):
                pass

        if api_devs:
            try:
                offset = 6 if api_devs["DEVS"][0]["ID"] in [6, 7, 8] else 0

                for board in api_devs["DEVS"]:
                    _id = board["ID"] - offset
                    hashrate = round(float(board["MHS 1m"] / 1000000), 2)
                    hashboards[_id].hashrate = hashrate
            except (IndexError, KeyError):
                pass

        return hashboards

    async def get_env_temp(self, *args, **kwargs) -> Optional[float]:
        return None

    async def get_wattage(
        self, api_tunerstatus: dict = None, graphql_wattage: dict = None
    ) -> Optional[int]:
        if not graphql_wattage and not api_tunerstatus:
            graphql_wattage = await self.send_graphql_query(
                "{bosminer{info{workSolver{power{approxConsumptionW}}}}}"
            )

        if graphql_wattage:
            try:
                return graphql_wattage["bosminer"]["info"]["workSolver"]["power"][
                    "approxConsumptionW"
                ]
            except KeyError:
                pass

        if not api_tunerstatus:
            api_tunerstatus = await self.api.tunerstatus()

        if api_tunerstatus:
            try:
                return api_tunerstatus["TUNERSTATUS"][0][
                    "ApproximateMinerPowerConsumption"
                ]
            except (KeyError, IndexError):
                pass

    async def get_wattage_limit(
        self, api_tunerstatus: dict = None, graphql_wattage_limit: dict = None
    ) -> Optional[int]:
        if not graphql_wattage_limit and not api_tunerstatus:
            graphql_wattage_limit = await self.send_graphql_query(
                "{bosminer{info{workSolver{power{limitW}}}}}"
            )

        if graphql_wattage_limit:
            try:
                return graphql_wattage_limit["bosminer"]["info"]["workSolver"]["power"][
                    "limitW"
                ]
            except KeyError:
                pass

        if not api_tunerstatus:
            api_tunerstatus = await self.api.tunerstatus()

        if api_tunerstatus:
            try:
                return api_tunerstatus["TUNERSTATUS"][0]["PowerLimit"]
            except (KeyError, IndexError):
                pass

    async def get_fans(
        self, api_fans: dict = None, graphql_fans: dict = None
    ) -> Tuple[
        Tuple[Optional[int], Optional[int], Optional[int], Optional[int]],
        Tuple[Optional[int]],
    ]:
        psu_fan = None

        fan_speeds = namedtuple("FanSpeeds", "fan_1 fan_2 fan_3 fan_4")
        psu_fan_speeds = namedtuple("PSUFanSpeeds", "psu_fan")
        miner_fan_speeds = namedtuple("MinerFans", "fan_speeds psu_fan_speeds")

        if not graphql_fans and not api_fans:
            graphql_fans = await self.send_graphql_query(
                "{bosminer{info{fans{name, rpm}}}"
            )

        if graphql_fans:
            fans = {"fan_1": None, "fan_2": None, "fan_3": None, "fan_4": None}
            for n in range(self.fan_count):
                try:
                    fans[f"fan_{n + 1}"] = graphql_fans["bosminer"]["info"]["fans"][n][
                        "rpm"
                    ]
                except KeyError:
                    pass
            return miner_fan_speeds(
                fan_speeds(fans["fan_1"], fans["fan_2"], fans["fan_3"], fans["fan_4"]),
                psu_fan_speeds(psu_fan),
            )

        if not api_fans:
            api_fans = await self.api.fans()

        if api_fans:
            fans = {"fan_1": None, "fan_2": None, "fan_3": None, "fan_4": None}
            for n in range(self.fan_count):
                try:
                    fans[f"fan_{n + 1}"] = api_fans["FANS"][n]["RPM"]
                except KeyError:
                    pass
            return miner_fan_speeds(
                fan_speeds(fans["fan_1"], fans["fan_2"], fans["fan_3"], fans["fan_4"]),
                psu_fan_speeds(psu_fan),
            )

    async def get_pools(
        self, api_pools: dict = None, graphql_pools: dict = None
    ) -> List[dict]:
        if not graphql_pools and not api_pools:
            graphql_pools = await self.send_graphql_query(
                "bosminer{config{... on BosminerConfig{groups{pools{urluser}strategy{... on QuotaStrategy{quota}}}}}"
            )

        if graphql_pools:
            groups = []
            try:
                g = graphql_pools["bosminer"]["config"]["groups"]
                for group in g:
                    pools = {"quota": group["strategy"]["quota"]}
                    for i, pool in enumerate(group["pools"]):
                        pools[f"pool_{i + 1}_url"] = (
                            pool["url"]
                            .replace("stratum+tcp://", "")
                            .replace("stratum2+tcp://", "")
                        )
                        pools[f"pool_{i + 1}_user"] = pool["user"]
                    groups.append(pools)
                return groups
            except KeyError:
                pass

        if not api_pools:
            api_pools = await self.api.pools()

        if api_pools:
            seen = []
            groups = [{"quota": "0"}]
            for i, pool in enumerate(api_pools["POOLS"]):
                if len(seen) == 0:
                    seen.append(pool["User"])
                if not pool["User"] in seen:
                    # need to use get_config, as this will never read perfectly as there are some bad edge cases
                    groups = []
                    cfg = await self.get_config()
                    for group in cfg.pool_groups:
                        pools = {"quota": group.quota}
                        for _i, _pool in enumerate(group.pools):
                            pools[f"pool_{_i + 1}_url"] = _pool.url.replace(
                                "stratum+tcp://", ""
                            ).replace("stratum2+tcp://", "")
                            pools[f"pool_{_i + 1}_user"] = _pool.username
                        groups.append(pools)
                    return groups
                else:
                    groups[0][f"pool_{i + 1}_url"] = (
                        pool["URL"]
                        .replace("stratum+tcp://", "")
                        .replace("stratum2+tcp://", "")
                    )
                    groups[0][f"pool_{i + 1}_user"] = pool["User"]
            return groups

    async def get_errors(
        self, api_tunerstatus: dict = None, graphql_errors: dict = None
    ) -> List[MinerErrorData]:
        if not graphql_errors and not api_tunerstatus:
            graphql_errors = await self.send_graphql_query(
                "{bosminer{info{workSolver{childSolvers{name, tuner{statusMessages}}}}}}"
            )

        if graphql_errors:
            errors = []
            try:
                boards = graphql_errors["bosminer"]["info"]["workSolver"][
                    "childSolvers"
                ]
            except (KeyError, IndexError):
                boards = None

            if boards:
                offset = 6 if int(boards[0]["name"]) in [6, 7, 8] else 0
                for hb in boards:
                    _id = int(hb["name"]) - offset
                    tuner = hb["tuner"]
                    if tuner:
                        if msg := tuner.get("statusMessages"):
                            if len(msg) > 0:
                                if hb["tuner"]["statusMessages"][0] not in [
                                    "Stable",
                                    "Testing performance profile",
                                    "Tuning individual chips",
                                ]:
                                    errors.append(
                                        BraiinsOSError(
                                            f"Slot {_id} {hb['tuner']['statusMessages'][0]}"
                                        )
                                    )

        if not api_tunerstatus:
            api_tunerstatus = await self.api.tunerstatus()

        if api_tunerstatus:
            errors = []
            try:
                chain_status = api_tunerstatus["TUNERSTATUS"][0]["TunerChainStatus"]
                if chain_status and len(chain_status) > 0:
                    offset = (
                        6 if int(chain_status[0]["HashchainIndex"]) in [6, 7, 8] else 0
                    )

                    for board in chain_status:
                        _id = board["HashchainIndex"] - offset
                        if board["Status"] not in [
                            "Stable",
                            "Testing performance profile",
                            "Tuning individual chips",
                        ]:
                            _error = board["Status"].split(" {")[0]
                            _error = _error[0].lower() + _error[1:]
                            errors.append(BraiinsOSError(f"Slot {_id} {_error}"))
                return errors
            except (KeyError, IndexError):
                pass

    async def get_fault_light(self, graphql_fault_light: dict = None) -> bool:
        if self.light:
            return self.light

        if not graphql_fault_light:
            if self.fw_ver:
                # fw version has to be greater than 21.09 and not 21.09
                if (
                    int(self.fw_ver.split(".")[0]) == 21
                    and int(self.fw_ver.split(".")[1]) > 9
                ) or int(self.fw_ver.split(".")[0]) > 21:
                    graphql_fault_light = await self.send_graphql_query(
                        "{bos {faultLight}}"
                    )
                else:
                    logging.info(
                        f"FW version {self.fw_ver} is too low for fault light info in graphql."
                    )
            else:
                # worth trying
                graphql_fault_light = await self.send_graphql_query(
                    "{bos {faultLight}}"
                )
                if graphql_fault_light.get("errors"):
                    if len(graphql_fault_light["errors"]) > 0:
                        # it did fail then
                        logging.debug("GraphQL fault light failed, likely due to version being too low (<=21.0.9)")

        # get light through GraphQL
        if graphql_fault_light:
            try:
                self.light = graphql_fault_light["bos"]["faultLight"]
                return self.light
            except (TypeError, KeyError, ValueError, IndexError):
                pass

        # get light via ssh if that fails (10x slower)
        try:
            data = (
                await self.send_ssh_command("cat /sys/class/leds/'Red LED'/delay_off")
            ).strip()
            self.light = False
            if data == "50":
                self.light = True
        except Exception as e:
            logging.debug(f"SSH command failed - Fault Light - {e}")
        return self.light

    async def _get_data(self, allow_warning: bool) -> dict:
        miner_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            try:
                miner_data = await self.api.multicommand(
                    "summary",
                    "temps",
                    "tunerstatus",
                    "pools",
                    "devdetails",
                    "fans",
                    "devs",
                    "version",
                    allow_warning=allow_warning,
                )
            except APIError as e:
                if str(e.message) == "Not ready":
                    try:
                        miner_data = await self.api.multicommand(
                            "summary", "tunerstatus", "pools", "devs", "version"
                        )
                    except APIError:
                        pass
            if miner_data:
                break
        if miner_data:
            summary = miner_data.get("summary")
            if summary:
                summary = summary[0]
            version = miner_data.get("version")
            if version:
                version = version[0]
            temps = miner_data.get("temps")
            if temps:
                temps = temps[0]
            tunerstatus = miner_data.get("tunerstatus")
            if tunerstatus:
                tunerstatus = tunerstatus[0]
            pools = miner_data.get("pools")
            if pools:
                pools = pools[0]
            devdetails = miner_data.get("devdetails")
            if devdetails:
                devdetails = devdetails[0]
            devs = miner_data.get("devs")
            if devs:
                devs = devs[0]
            fans = miner_data.get("fans")
            if fans:
                fans = fans[0]
        else:
            summary, version, temps, tunerstatus, pools, devdetails, devs, fans = (None for _ in range(8))
        gql_data = await self.send_graphql_query(
            "{bos {hostname}, bosminer{config{... on BosminerConfig{groups{pools{url, user}, strategy{... on QuotaStrategy {quota}}}}}, info{fans{name, rpm}, workSolver{realHashrate{mhs1M}, temperatures{degreesC}, power{limitW, approxConsumptionW}, childSolvers{name, realHashrate{mhs1M}, hwDetails{chips}, tuner{statusMessages}, temperatures{degreesC}}}}}}"
        )
        if gql_data:
            if "data" in gql_data:
                gql_data = gql_data["data"]

        data = {  # noqa - Ignore dictioonary could be re-written
            # ip - Done at start
            # datetime - Done auto
            "mac": await self.get_mac(),
            "model": await self.get_model(),
            # make - Done at start
            # api_ver - Done at end
            # fw_ver - Done at end
            "hostname": await self.get_hostname(graphql_hostname=gql_data),
            "hashrate": await self.get_hashrate(
                api_summary=summary, graphql_hashrate=gql_data
            ),
            "hashboards": await self.get_hashboards(
                api_temps=temps,
                api_devdetails=devdetails,
                api_devs=devs,
                graphql_boards=gql_data,
            ),
            # ideal_hashboards - Done at start
            "env_temp": await self.get_env_temp(),
            "wattage": await self.get_wattage(
                api_tunerstatus=tunerstatus, graphql_wattage=gql_data
            ),
            "wattage_limit": await self.get_wattage_limit(
                api_tunerstatus=tunerstatus, graphql_wattage_limit=gql_data
            ),
            # fan_1 - Done at end
            # fan_2 - Done at end
            # fan_3 - Done at end
            # fan_4 - Done at end
            # fan_psu - Done at end
            # ideal_chips - Done at start
            # pool_split - Done at end
            # pool_1_url - Done at end
            # pool_1_user - Done at end
            # pool_2_url - Done at end
            # pool_2_user - Done at end
            "errors": await self.get_errors(
                api_tunerstatus=tunerstatus, graphql_errors=gql_data
            ),
            "fault_light": await self.get_fault_light(),
        }

        data["api_ver"], data["fw_ver"] = await self.get_version(
            api_version=version, graphql_version=gql_data
        )
        fan_data = await self.get_fans(api_fans=fans, graphql_fans=gql_data)

        data["fan_1"] = fan_data.fan_speeds.fan_1  # noqa
        data["fan_2"] = fan_data.fan_speeds.fan_2  # noqa
        data["fan_3"] = fan_data.fan_speeds.fan_3  # noqa
        data["fan_4"] = fan_data.fan_speeds.fan_4  # noqa

        data["fan_psu"] = fan_data.psu_fan_speeds.psu_fan # noqa

        pools_data = await self.get_pools(api_pools=pools, graphql_pools=gql_data)
        data["pool_1_url"] = pools_data[0]["pool_1_url"]
        data["pool_1_user"] = pools_data[0]["pool_1_user"]
        if len(pools_data) > 1:
            data["pool_2_url"] = pools_data[1]["pool_1_url"]
            data["pool_2_user"] = pools_data[1]["pool_1_user"]
            data["pool_split"] = f"{pools_data[0]['quota']}/{pools_data[1]['quota']}"
        else:
            try:
                data["pool_2_url"] = pools_data[0]["pool_1_url"]
                data["pool_2_user"] = pools_data[0]["pool_1_user"]
                data["quota"] = "0"
            except KeyError:
                pass

        return data
