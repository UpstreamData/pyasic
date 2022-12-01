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
from typing import List, Union

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
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = BOSMinerAPI(ip)
        self.api_type = "BOSMiner"
        self.uname = "root"
        self.pwd = "admin"
        self.config = None

    async def send_ssh_command(self, cmd: str) -> Union[str, None]:
        """Send a command to the miner over ssh.

        Returns:
            Result of the command or None.
        """
        result = None

        # open an ssh connection
        async with (await self._get_ssh_connection()) as conn:
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
        return str(result)

    async def send_graphql_query(self, query) -> Union[dict, None]:
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

    async def get_hostname(self) -> str:
        """Get miner hostname.

        Returns:
            The hostname of the miner as a string or "?"
        """
        if self.hostname:
            return self.hostname
        # get hostname through GraphQL
        if data := await self.send_graphql_query("{bos {hostname}}"):
            self.hostname = data["data"]["bos"]["hostname"]
            return self.hostname

        try:
            async with (await self._get_ssh_connection()) as conn:
                if conn is not None:
                    data = await conn.run("cat /proc/sys/kernel/hostname")
                    host = data.stdout.strip()
                    logging.debug(f"Found hostname for {self.ip}: {host}")
                    self.hostname = host
                    return self.hostname
                else:
                    logging.warning(f"Failed to get hostname for miner: {self}")
                    return "?"
        except Exception:
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"

    async def get_model(self) -> Union[str, None]:
        """Get miner model.

        Returns:
            Miner model or None.
        """
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

    async def get_version(self) -> Union[str, None]:
        """Get miner firmware version.

        Returns:
            Miner firmware version or None.
        """
        # check if version is cached
        if self.version:
            logging.debug(f"Found version for {self.ip}: {self.version}")
            return self.version
        version_data = None
        # try to get data from graphql
        data = await self.send_graphql_query("{bos{info{version{full}}}}")
        if data:
            version_data = data["bos"]["info"]["version"]["full"]

        if not version_data:
            # try version data file
            version_data = await self.send_ssh_command("cat /etc/bos_version")

        # if we get the version data, parse it
        if version_data:
            self.version = version_data.split("-")[5]
            logging.debug(f"Found version for {self.ip}: {self.version}")
            return self.version

        # if we fail to get version, log a failed attempt
        logging.warning(f"Failed to get model for miner: {self}")
        return None

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

    async def check_light(self) -> bool:
        if self.light:
            return self.light
        # get light through GraphQL
        if data := await self.send_graphql_query("{bos {faultLight}}"):
            try:
                self.light = data["data"]["bos"]["faultLight"]
                return self.light
            except (TypeError, KeyError, ValueError, IndexError):
                pass

        # get light via ssh if that fails (10x slower)
        data = (
            await self.send_ssh_command("cat /sys/class/leds/'Red LED'/delay_off")
        ).strip()
        self.light = False
        if data == "50":
            self.light = True
        return self.light

    async def get_errors(self) -> List[MinerErrorData]:
        tunerstatus = None
        errors = []

        try:
            tunerstatus = await self.api.tunerstatus()
        except Exception as e:
            logging.warning(e)

        if tunerstatus:
            try:
                tuner = tunerstatus[0].get("TUNERSTATUS")
            except KeyError:
                tuner = tunerstatus.get("TUNERSTATUS")
            if tuner:
                if len(tuner) > 0:
                    chain_status = tuner[0].get("TunerChainStatus")
                    if chain_status and len(chain_status) > 0:
                        board_map = {
                            0: "Left board",
                            1: "Center board",
                            2: "Right board",
                        }
                        offset = (
                            6
                            if chain_status[0]["HashchainIndex"] in [6, 7, 8]
                            else chain_status[0]["HashchainIndex"]
                        )
                        for board in chain_status:
                            _id = board["HashchainIndex"] - offset
                            if board["Status"] not in [
                                "Stable",
                                "Testing performance profile",
                                "Tuning individual chips"
                            ]:
                                _error = board["Status"].split(" {")[0]
                                _error = _error[0].lower() + _error[1:]
                                errors.append(
                                    BraiinsOSError(f"{board_map[_id]} {_error}")
                                )
        return errors

    async def get_data(self, allow_warning: bool = True) -> MinerData:
        """Get data from the miner.

        Returns:
            A [`MinerData`][pyasic.data.MinerData] instance containing the miners data.
        """
        d = await self._graphql_get_data()
        if d:
            return d

        data = MinerData(
            ip=str(self.ip),
            ideal_chips=self.nominal_chips * self.ideal_hashboards,
            ideal_hashboards=self.ideal_hashboards,
            hashboards=[
                HashBoard(slot=i, expected_chips=self.nominal_chips)
                for i in range(self.ideal_hashboards)
            ],
        )

        model = await self.get_model()
        hostname = await self.get_hostname()
        mac = await self.get_mac()

        if model:
            data.model = model

        if hostname:
            data.hostname = hostname

        if mac:
            data.mac = mac

        data.fault_light = await self.check_light()

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
                    allow_warning=allow_warning,
                )
            except APIError as e:
                if str(e.message) == "Not ready":
                    miner_data = await self.api.multicommand(
                        "summary", "tunerstatus", "pools", "devs"
                    )
            if miner_data:
                break
        if not miner_data:
            return data
        summary = miner_data.get("summary")
        temps = miner_data.get("temps")
        tunerstatus = miner_data.get("tunerstatus")
        pools = miner_data.get("pools")
        devdetails = miner_data.get("devdetails")
        devs = miner_data.get("devs")
        fans = miner_data.get("fans")

        if summary:
            hr = summary[0].get("SUMMARY")
            if hr:
                if len(hr) > 0:
                    hr = hr[0].get("MHS 1m")
                    if hr:
                        data.hashrate = round(hr / 1000000, 2)

        if temps:
            temp = temps[0].get("TEMPS")
            if temp:
                if len(temp) > 0:
                    offset = 6 if temp[0]["ID"] in [6, 7, 8] else temp[0]["ID"]
                    for board in temp:
                        _id = board["ID"] - offset
                        chip_temp = round(board["Chip"])
                        board_temp = round(board["Board"])
                        data.hashboards[_id].chip_temp = chip_temp
                        data.hashboards[_id].temp = board_temp

        if fans:
            fan_data = fans[0].get("FANS")
            if fan_data:
                for fan in range(self.fan_count):
                    setattr(data, f"fan_{fan+1}", fan_data[fan]["RPM"])

        if pools:
            pool_1 = None
            pool_2 = None
            pool_1_user = None
            pool_2_user = None
            pool_1_quota = 1
            pool_2_quota = 1
            quota = 0
            for pool in pools[0].get("POOLS"):
                if not pool_1_user:
                    pool_1_user = pool.get("User")
                    pool_1 = pool["URL"]
                    pool_1_quota = pool["Quota"]
                elif not pool_2_user:
                    pool_2_user = pool.get("User")
                    pool_2 = pool["URL"]
                    pool_2_quota = pool["Quota"]
                if not pool.get("User") == pool_1_user:
                    if not pool_2_user == pool.get("User"):
                        pool_2_user = pool.get("User")
                        pool_2 = pool["URL"]
                        pool_2_quota = pool["Quota"]
            if pool_2_user and not pool_2_user == pool_1_user:
                quota = f"{pool_1_quota}/{pool_2_quota}"

            if pool_1:
                pool_1 = pool_1.replace("stratum+tcp://", "").replace(
                    "stratum2+tcp://", ""
                )
                data.pool_1_url = pool_1

            if pool_1_user:
                data.pool_1_user = pool_1_user

            if pool_2:
                pool_2 = pool_2.replace("stratum+tcp://", "").replace(
                    "stratum2+tcp://", ""
                )
                data.pool_2_url = pool_2

            if pool_2_user:
                data.pool_2_user = pool_2_user

            if quota:
                data.pool_split = str(quota)

        if tunerstatus:
            tuner = tunerstatus[0].get("TUNERSTATUS")
            if tuner:
                if len(tuner) > 0:
                    wattage = tuner[0].get("ApproximateMinerPowerConsumption")
                    wattage_limit = tuner[0].get("PowerLimit")
                    if wattage_limit:
                        data.wattage_limit = wattage_limit
                    if wattage is not None:
                        data.wattage = wattage

                    chain_status = tuner[0].get("TunerChainStatus")
                    if chain_status and len(chain_status) > 0:
                        board_map = {
                            0: "Left board",
                            1: "Center board",
                            2: "Right board",
                        }
                        offset = (
                            6
                            if chain_status[0]["HashchainIndex"] in [6, 7, 8]
                            else chain_status[0]["HashchainIndex"]
                        )
                        for board in chain_status:
                            _id = board["HashchainIndex"] - offset
                            if board["Status"] not in [
                                "Stable",
                                "Testing performance profile",
                            ]:
                                _error = board["Status"].split(" {")[0]
                                _error = _error[0].lower() + _error[1:]
                                data.errors.append(
                                    BraiinsOSError(f"{board_map[_id]} {_error}")
                                )

        if devdetails:
            boards = devdetails[0].get("DEVDETAILS")
            if boards:
                if len(boards) > 0:
                    offset = 6 if boards[0]["ID"] in [6, 7, 8] else boards[0]["ID"]
                    for board in boards:
                        _id = board["ID"] - offset
                        chips = board["Chips"]
                        data.hashboards[_id].chips = chips
                        if chips > 0:
                            data.hashboards[_id].missing = False
                        else:
                            data.hashboards[_id].missing = True

        if devs:
            boards = devs[0].get("DEVS")
            if boards:
                if len(boards) > 0:
                    offset = 6 if boards[0]["ID"] in [6, 7, 8] else boards[0]["ID"]
                    for board in boards:
                        _id = board["ID"] - offset
                        hashrate = round(board["MHS 1m"] / 1000000, 2)
                        data.hashboards[_id].hashrate = hashrate
        return data

    async def _graphql_get_data(self) -> Union[MinerData, None]:
        data = MinerData(
            ip=str(self.ip),
            ideal_chips=self.nominal_chips * self.ideal_hashboards,
            ideal_hashboards=self.ideal_hashboards,
            hashboards=[
                HashBoard(slot=i, expected_chips=self.nominal_chips, missing=True)
                for i in range(self.ideal_hashboards)
            ],
        )
        query = "{bos {hostname}, bosminer{config{... on BosminerConfig{groups{pools{url, user}, strategy{... on QuotaStrategy {quota}}}}}, info{fans{name, rpm}, workSolver{realHashrate{mhs1M}, temperatures{degreesC}, power{limitW, approxConsumptionW}, childSolvers{name, realHashrate{mhs1M}, hwDetails{chips}, tuner{statusMessages}, temperatures{degreesC}}}}}}"
        query_data = await self.send_graphql_query(query)
        if not query_data:
            return None
        query_data = query_data["data"]
        if not query_data:
            return None

        data.mac = await self.get_mac()
        data.model = await self.get_model()
        if query_data.get("bos"):
            if query_data["bos"].get("hostname"):
                data.hostname = query_data["bos"]["hostname"]

        try:
            if query_data["bosminer"]["info"]["workSolver"]["realHashrate"].get("mhs1M"):
                data.hashrate = round(
                    query_data["bosminer"]["info"]["workSolver"]["realHashrate"]["mhs1M"]
                    / 1000000,
                    2,
                )
        except (TypeError, KeyError, ValueError, IndexError):
            pass

        boards = None
        if query_data.get("bosminer"):
            if query_data["bosminer"].get("info"):
                if query_data["bosminer"]["info"].get("workSolver"):
                    boards = query_data["bosminer"]["info"]["workSolver"].get("childSolvers")
        if boards:
            offset = 6 if int(boards[0]["name"]) in [6, 7, 8] else int(boards[0]["name"])
            for hb in boards:
                _id = int(hb["name"]) - offset

                board = data.hashboards[_id]
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

                tuner = hb.get("tuner")
                if tuner:
                    if msg := tuner.get("statusMessages"):
                        if len(msg) > 0:
                            if hb["tuner"]["statusMessages"][0] not in [
                                "Stable",
                                "Testing performance profile",
                                "Tuning individual chips"
                            ]:
                                data.errors.append(
                                    BraiinsOSError(f"Slot {_id} {hb['tuner']['statusMessages'][0]}")
                                )
        try:
            data.wattage = query_data["bosminer"]["info"]["workSolver"]["power"]["approxConsumptionW"]
        except (TypeError, KeyError, ValueError, IndexError):
            data.wattage = 0
        try:
            data.wattage_limit = query_data["bosminer"]["info"]["workSolver"]["power"]["limitW"]
        except (TypeError, KeyError, ValueError, IndexError):
            pass


        for n in range(self.fan_count):
            try:
                setattr(data, f"fan_{n + 1}", query_data["bosminer"]["info"]["fans"][n]["rpm"])
            except (TypeError, KeyError, ValueError, IndexError):
                pass

        groups = None
        if query_data.get("bosminer"):
            if query_data["bosminer"].get("config"):
                groups = query_data["bosminer"]["config"].get("groups")
        if groups:
            if len(groups) == 1:
                try:
                    data.pool_1_user = groups[0]["pools"][0]["user"]
                except (TypeError, KeyError, ValueError, IndexError):
                    pass
                try:
                    data.pool_1_url = groups[0]["pools"][0]["url"]
                except (TypeError, KeyError, ValueError, IndexError):
                    pass
                try:
                    data.pool_2_user = groups[0]["pools"][1]["user"]
                except (TypeError, KeyError, ValueError, IndexError):
                    pass
                try:
                    data.pool_2_url = groups[0]["pools"][1]["url"]
                except (TypeError, KeyError, ValueError, IndexError):
                    pass
                data.quota = 0
            else:
                try:
                    data.pool_1_user = groups[0]["pools"][0]["user"]
                except (TypeError, KeyError, ValueError, IndexError):
                    pass
                try:
                    data.pool_1_url = groups[0]["pools"][0]["url"]
                except (TypeError, KeyError, ValueError, IndexError):
                    pass
                try:
                    data.pool_2_user = groups[1]["pools"][0]["user"]
                except (TypeError, KeyError, ValueError, IndexError):
                    pass
                try:
                    data.pool_2_url = groups[1]["pools"][0]["url"]
                except (TypeError, KeyError, ValueError, IndexError):
                    pass
                if groups[0]["strategy"].get("quota"):
                    data.quota = str(groups[0]["strategy"]["quota"]) + "/" + str(groups[1]["strategy"]["quota"])

        data.fault_light = await self.check_light()

        return data

    async def get_mac(self):
        result = await self.send_ssh_command("cat /sys/class/net/eth0/address")
        return result.upper().strip()

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
