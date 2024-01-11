# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------
import asyncio
import logging
import time
from collections import namedtuple
from typing import List, Optional, Tuple, Union

import toml

from pyasic.API.bosminer import BOSMinerAPI
from pyasic.config import MinerConfig
from pyasic.config.mining import MiningModePowerTune
from pyasic.data import Fan, HashBoard
from pyasic.data.error_codes import BraiinsOSError, MinerErrorData
from pyasic.errors import APIError
from pyasic.miners.base import (
    BaseMiner,
    DataFunction,
    DataLocations,
    DataOptions,
    GraphQLCommand,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.web.braiins_os import BOSerWebAPI, BOSMinerWebAPI

BOSMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "get_mac",
            [WebAPICommand("web_net_conf", "admin/network/iface_status/lan")],
        ),
        str(DataOptions.MODEL): DataFunction("get_model"),
        str(DataOptions.API_VERSION): DataFunction(
            "get_api_ver", [RPCAPICommand("api_version", "version")]
        ),
        str(DataOptions.FW_VERSION): DataFunction("get_fw_ver"),
        str(DataOptions.HOSTNAME): DataFunction("get_hostname"),
        str(DataOptions.HASHRATE): DataFunction(
            "get_hashrate",
            [RPCAPICommand("api_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "get_expected_hashrate", [RPCAPICommand("api_devs", "devs")]
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "get_hashboards",
            [
                RPCAPICommand("api_temps", "temps"),
                RPCAPICommand("api_devdetails", "devdetails"),
                RPCAPICommand("api_devs", "devs"),
            ],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction("get_env_temp"),
        str(DataOptions.WATTAGE): DataFunction(
            "get_wattage",
            [RPCAPICommand("api_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "get_wattage_limit",
            [RPCAPICommand("api_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.FANS): DataFunction(
            "get_fans",
            [RPCAPICommand("api_fans", "fans")],
        ),
        str(DataOptions.FAN_PSU): DataFunction("get_fan_psu"),
        str(DataOptions.ERRORS): DataFunction(
            "get_errors",
            [RPCAPICommand("api_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction("get_fault_light"),
        str(DataOptions.IS_MINING): DataFunction(
            "is_mining", [RPCAPICommand("api_devdetails", "devdetails")]
        ),
        str(DataOptions.UPTIME): DataFunction(
            "get_uptime", [RPCAPICommand("api_summary", "summary")]
        ),
        str(DataOptions.CONFIG): DataFunction("get_config"),
    }
)


class BOSMiner(BaseMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip)
        # interfaces
        self.api = BOSMinerAPI(ip, api_ver)
        self.web = BOSMinerWebAPI(ip)

        # static data
        self.api_type = "BOSMiner"
        # data gathering locations
        self.data_locations = BOSMINER_DATA_LOC
        # autotuning/shutdown support
        self.supports_autotuning = True
        self.supports_shutdown = True

        # data storage
        self.api_ver = api_ver

    async def send_ssh_command(self, cmd: str) -> Optional[str]:
        result = None

        try:
            conn = await asyncio.wait_for(self._get_ssh_connection(), timeout=10)
        except (ConnectionError, asyncio.TimeoutError):
            return None

        # open an ssh connection
        async with conn:
            # 3 retries
            for i in range(3):
                try:
                    # run the command and get the result
                    result = await conn.run(cmd)
                    stderr = result.stderr
                    result = result.stdout

                    if len(stderr) > len(result):
                        result = stderr

                except Exception as e:
                    # if the command fails, log it
                    logging.warning(f"{self} command {cmd} error: {e}")

                    # on the 3rd retry, return None
                    if i == 3:
                        return
                    continue
        # return the result, either command output or None
        return result

    async def fault_light_on(self) -> bool:
        logging.debug(f"{self}: Sending fault_light on command.")
        ret = await self.send_ssh_command("miner fault_light on")
        logging.debug(f"{self}: fault_light on command completed.")
        if isinstance(ret, str):
            self.light = True
            return self.light
        return False

    async def fault_light_off(self) -> bool:
        logging.debug(f"{self}: Sending fault_light off command.")
        self.light = False
        ret = await self.send_ssh_command("miner fault_light off")
        logging.debug(f"{self}: fault_light off command completed.")
        if isinstance(ret, str):
            self.light = False
            return True
        return False

    async def restart_backend(self) -> bool:
        return await self.restart_bosminer()

    async def restart_bosminer(self) -> bool:
        logging.debug(f"{self}: Sending bosminer restart command.")
        ret = await self.send_ssh_command("/etc/init.d/bosminer restart")
        logging.debug(f"{self}: bosminer restart command completed.")
        if isinstance(ret, str):
            return True
        return False

    async def stop_mining(self) -> bool:
        try:
            data = await self.api.pause()
        except APIError:
            return False
        if data.get("PAUSE"):
            if data["PAUSE"][0]:
                return True
        return False

    async def resume_mining(self) -> bool:
        try:
            data = await self.api.resume()
        except APIError:
            return False
        if data.get("RESUME"):
            if data["RESUME"][0]:
                return True
        return False

    async def reboot(self) -> bool:
        logging.debug(f"{self}: Sending reboot command.")
        ret = await self.send_ssh_command("/sbin/reboot")
        logging.debug(f"{self}: Reboot command completed.")
        if isinstance(ret, str):
            return True
        return False

    async def get_config(self) -> MinerConfig:
        logging.debug(f"{self}: Getting config.")

        try:
            conn = await self._get_ssh_connection()
        except ConnectionError:
            conn = None

        if conn:
            async with conn:
                # good ol' BBB compatibility :/
                toml_data = toml.loads(
                    (await conn.run("cat /etc/bosminer.toml")).stdout
                )
            logging.debug(f"{self}: Converting config file.")
            cfg = MinerConfig.from_bosminer(toml_data)
            self.config = cfg
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        logging.debug(f"{self}: Sending config.")
        self.config = config

        toml_conf = toml.dumps(
            {
                "format": {
                    "version": "1.2+",
                    "generator": "pyasic",
                    "model": f"{self.make.replace('Miner', 'miner')} {self.model.replace(' (BOS)', '').replace('j', 'J')}",
                    "timestamp": int(time.time()),
                },
                **config.as_bosminer(user_suffix=user_suffix),
            }
        )
        try:
            conn = await self._get_ssh_connection()
        except ConnectionError as e:
            raise APIError("SSH connection failed when sending config.") from e
        async with conn:
            # BBB check because bitmain suxx
            bbb_check = await conn.run(
                "if [ ! -f /etc/init.d/bosminer ]; then echo '1'; else echo '0'; fi;"
            )

            bbb = bbb_check.stdout.strip() == "1"

            if not bbb:
                await conn.run("/etc/init.d/bosminer stop")
                logging.debug(f"{self}: Opening SFTP connection.")
                async with conn.start_sftp_client() as sftp:
                    logging.debug(f"{self}: Opening config file.")
                    async with sftp.open("/etc/bosminer.toml", "w+") as file:
                        await file.write(toml_conf)
                logging.debug(f"{self}: Restarting BOSMiner")
                await conn.run("/etc/init.d/bosminer start")

            # I really hate BBB, please get rid of it if you have it
            else:
                await conn.run("/etc/init.d/S99bosminer stop")
                logging.debug(f"{self}: BBB sending config")
                await conn.run("echo '" + toml_conf + "' > /etc/bosminer.toml")
                logging.debug(f"{self}: BBB restarting bosminer.")
                await conn.run("/etc/init.d/S99bosminer start")

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            cfg = await self.get_config()
            if cfg is None:
                return False
            cfg.mining_mode = MiningModePowerTune(wattage)
            await self.send_config(cfg)
        except Exception as e:
            logging.warning(f"{self} set_power_limit: {e}")
            return False
        else:
            return True

    async def set_static_ip(
        self,
        ip: str,
        dns: str,
        gateway: str,
        subnet_mask: str = "255.255.255.0",
    ):
        cfg_data_lan = (
            "config interface 'lan'\n\toption type 'bridge'\n\toption ifname 'eth0'\n\toption proto 'static'\n\toption ipaddr '"
            + ip
            + "'\n\toption netmask '"
            + subnet_mask
            + "'\n\toption gateway '"
            + gateway
            + "'\n\toption dns '"
            + dns
            + "'"
        )
        data = await self.send_ssh_command("cat /etc/config/network")

        split_data = data.split("\n\n")
        for idx in range(len(split_data)):
            if "config interface 'lan'" in split_data[idx]:
                split_data[idx] = cfg_data_lan
        config = "\n\n".join(split_data)

        conn = await self._get_ssh_connection()

        async with conn:
            await conn.run("echo '" + config + "' > /etc/config/network")

    async def set_dhcp(self):
        cfg_data_lan = "config interface 'lan'\n\toption type 'bridge'\n\toption ifname 'eth0'\n\toption proto 'dhcp'"
        data = await self.send_ssh_command("cat /etc/config/network")

        split_data = data.split("\n\n")
        for idx in range(len(split_data)):
            if "config interface 'lan'" in split_data[idx]:
                split_data[idx] = cfg_data_lan
        config = "\n\n".join(split_data)

        conn = await self._get_ssh_connection()

        async with conn:
            await conn.run("echo '" + config + "' > /etc/config/network")

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(self, web_net_conf: Union[dict, list] = None) -> Optional[str]:
        if not web_net_conf:
            try:
                web_net_conf = await self.web.luci.send_command(
                    "admin/network/iface_status/lan"
                )
            except APIError:
                pass

        if isinstance(web_net_conf, dict):
            if "admin/network/iface_status/lan" in web_net_conf.keys():
                web_net_conf = web_net_conf["admin/network/iface_status/lan"]

        if web_net_conf:
            try:
                return web_net_conf[0]["macaddr"]
            except LookupError:
                pass
        # could use ssh, but its slow and buggy
        # result = await self.send_ssh_command("cat /sys/class/net/eth0/address")
        # if result:
        #     return result.upper().strip()

    async def get_model(self) -> Optional[str]:
        if self.model is not None:
            return self.model + " (BOS)"
        return "? (BOS)"

    async def get_version(
        self, api_version: dict = None, graphql_version: dict = None
    ) -> Tuple[Optional[str], Optional[str]]:
        miner_version = namedtuple("MinerVersion", "api_ver fw_ver")
        api_ver_t = asyncio.create_task(self.get_api_ver(api_version))
        fw_ver_t = asyncio.create_task(self.get_fw_ver())
        await asyncio.gather(api_ver_t, fw_ver_t)
        return miner_version(api_ver=api_ver_t.result(), fw_ver=fw_ver_t.result())

    async def get_api_ver(self, api_version: dict = None) -> Optional[str]:
        if not api_version:
            try:
                api_version = await self.api.version()
            except APIError:
                pass

        # Now get the API version
        if api_version:
            try:
                api_ver = api_version["VERSION"][0]["API"]
            except (KeyError, IndexError):
                api_ver = None
            self.api_ver = api_ver
            self.api.api_ver = self.api_ver

        return self.api_ver

    async def get_fw_ver(self) -> Optional[str]:
        fw_ver = await self.send_ssh_command("cat /etc/bos_version")

        # if we get the version data, parse it
        if fw_ver is not None:
            ver = fw_ver.split("-")[5]
            if "." in ver:
                self.fw_ver = ver
                logging.debug(f"Found version for {self.ip}: {self.fw_ver}")

        return self.fw_ver

    async def get_hostname(self) -> Union[str, None]:
        try:
            hostname = (
                await self.send_ssh_command("cat /proc/sys/kernel/hostname")
            ).strip()
        except Exception as e:
            logging.error(f"BOSMiner get_hostname failed with error: {e}")
            return None
        return hostname

    async def get_hashrate(self, api_summary: dict = None) -> Optional[float]:
        # get hr from API
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

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
    ):
        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        cmds = []
        if not api_temps:
            cmds.append("temps")
        if not api_devdetails:
            cmds.append("devdetails")
        if not api_devs:
            cmds.append("devs")
        if len(cmds) > 0:
            try:
                d = await self.api.multicommand(*cmds)
            except APIError:
                d = {}
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
                offset = 6 if api_temps["TEMPS"][0]["ID"] in [6, 7, 8] else 1

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
                offset = 6 if api_devdetails["DEVDETAILS"][0]["ID"] in [6, 7, 8] else 1

                for board in api_devdetails["DEVDETAILS"]:
                    _id = board["ID"] - offset
                    chips = board["Chips"]
                    hashboards[_id].chips = chips
                    hashboards[_id].missing = False
            except (IndexError, KeyError):
                pass

        if api_devs:
            try:
                offset = 6 if api_devs["DEVS"][0]["ID"] in [6, 7, 8] else 1

                for board in api_devs["DEVS"]:
                    _id = board["ID"] - offset
                    hashrate = round(float(board["MHS 1m"] / 1000000), 2)
                    hashboards[_id].hashrate = hashrate
            except (IndexError, KeyError):
                pass

        return hashboards

    async def get_env_temp(self) -> Optional[float]:
        return None

    async def get_wattage(self, api_tunerstatus: dict = None) -> Optional[int]:
        if not api_tunerstatus:
            try:
                api_tunerstatus = await self.api.tunerstatus()
            except APIError:
                pass

        if api_tunerstatus:
            try:
                return api_tunerstatus["TUNERSTATUS"][0][
                    "ApproximateMinerPowerConsumption"
                ]
            except (KeyError, IndexError):
                pass

    async def get_wattage_limit(self, api_tunerstatus: dict = None) -> Optional[int]:
        if not api_tunerstatus:
            try:
                api_tunerstatus = await self.api.tunerstatus()
            except APIError:
                pass

        if api_tunerstatus:
            try:
                return api_tunerstatus["TUNERSTATUS"][0]["PowerLimit"]
            except (KeyError, IndexError):
                pass

    async def get_fans(self, api_fans: dict = None) -> List[Fan]:
        if not api_fans:
            try:
                api_fans = await self.api.fans()
            except APIError:
                pass

        if api_fans:
            fans = []
            for n in range(self.fan_count):
                try:
                    fans.append(Fan(api_fans["FANS"][n]["RPM"]))
                except (IndexError, KeyError):
                    pass
            return fans
        return [Fan() for _ in range(self.fan_count)]

    async def get_fan_psu(self) -> Optional[int]:
        return None

    async def get_errors(self, api_tunerstatus: dict = None) -> List[MinerErrorData]:
        if not api_tunerstatus:
            try:
                api_tunerstatus = await self.api.tunerstatus()
            except APIError:
                pass

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
        try:
            data = (
                await self.send_ssh_command("cat /sys/class/leds/'Red LED'/delay_off")
            ).strip()
            self.light = False
            if data == "50":
                self.light = True
            return self.light
        except (TypeError, AttributeError):
            return self.light

    async def get_expected_hashrate(self, api_devs: dict = None) -> Optional[float]:
        if not api_devs:
            try:
                api_devs = await self.api.devs()
            except APIError:
                pass

        if api_devs:
            try:
                offset = 6 if api_devs["DEVS"][0]["ID"] in [6, 7, 8] else 0
                hr_list = []

                for board in api_devs["DEVS"]:
                    _id = board["ID"] - offset
                    expected_hashrate = round(float(board["Nominal MHS"] / 1000000), 2)
                    if expected_hashrate:
                        hr_list.append(expected_hashrate)
                if len(hr_list) == 0:
                    return 0
                else:
                    return round(
                        (sum(hr_list) / len(hr_list)) * self.expected_hashboards, 2
                    )
            except (IndexError, KeyError):
                pass

    async def is_mining(self, api_devdetails: dict = None) -> Optional[bool]:
        if not api_devdetails:
            try:
                api_devdetails = await self.api.send_command(
                    "devdetails", ignore_errors=True, allow_warning=False
                )
            except APIError:
                pass

        if api_devdetails:
            try:
                return not api_devdetails["STATUS"][0]["Msg"] == "Unavailable"
            except LookupError:
                pass

    async def get_uptime(self, api_summary: dict = None) -> Optional[int]:
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return int(api_summary["SUMMARY"][0]["Elapsed"])
            except LookupError:
                pass


BOSER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "get_mac",
            [WebAPICommand("web_net_conf", "admin/network/iface_status/lan")],
        ),
        str(DataOptions.MODEL): DataFunction("get_model"),
        str(DataOptions.API_VERSION): DataFunction(
            "get_api_ver", [RPCAPICommand("api_version", "version")]
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "get_fw_ver",
            [
                GraphQLCommand(
                    "graphql_version", {"bos": {"info": {"version": {"full": None}}}}
                )
            ],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "get_hostname",
            [GraphQLCommand("graphql_hostname", {"bos": {"hostname": None}})],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "get_hashrate",
            [
                RPCAPICommand("api_summary", "summary"),
                GraphQLCommand(
                    "graphql_hashrate",
                    {
                        "bosminer": {
                            "info": {"workSolver": {"realHashrate": {"mhs1M": None}}}
                        }
                    },
                ),
            ],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "get_expected_hashrate", [RPCAPICommand("api_devs", "devs")]
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "get_hashboards",
            [
                RPCAPICommand("api_temps", "temps"),
                RPCAPICommand("api_devdetails", "devdetails"),
                RPCAPICommand("api_devs", "devs"),
                GraphQLCommand(
                    "graphql_boards",
                    {
                        "bosminer": {
                            "info": {
                                "workSolver": {
                                    "childSolvers": {
                                        "name": None,
                                        "realHashrate": {"mhs1M": None},
                                        "hwDetails": {"chips": None},
                                        "temperatures": {"degreesC": None},
                                    }
                                }
                            }
                        }
                    },
                ),
            ],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction("get_env_temp"),
        str(DataOptions.WATTAGE): DataFunction(
            "get_wattage",
            [
                RPCAPICommand("api_tunerstatus", "tunerstatus"),
                GraphQLCommand(
                    "graphql_wattage",
                    {
                        "bosminer": {
                            "info": {
                                "workSolver": {"power": {"approxConsumptionW": None}}
                            }
                        }
                    },
                ),
            ],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "get_wattage_limit",
            [
                RPCAPICommand("api_tunerstatus", "tunerstatus"),
                GraphQLCommand(
                    "graphql_wattage_limit",
                    {"bosminer": {"info": {"workSolver": {"power": {"limitW": None}}}}},
                ),
            ],
        ),
        str(DataOptions.FANS): DataFunction(
            "get_fans",
            [
                RPCAPICommand("api_fans", "fans"),
                GraphQLCommand(
                    "graphql_fans",
                    {"bosminer": {"info": {"fans": {"name": None, "rpm": None}}}},
                ),
            ],
        ),
        str(DataOptions.FAN_PSU): DataFunction("get_fan_psu"),
        str(DataOptions.ERRORS): DataFunction(
            "get_errors",
            [
                RPCAPICommand("api_tunerstatus", "tunerstatus"),
                GraphQLCommand(
                    "graphql_errors",
                    {
                        "bosminer": {
                            "info": {
                                "workSolver": {
                                    "childSolvers": {
                                        "name": None,
                                        "tuner": {"statusMessages": None},
                                    }
                                }
                            }
                        }
                    },
                ),
            ],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "get_fault_light",
            [GraphQLCommand("graphql_fault_light", {"bos": {"faultLight": None}})],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "is_mining", [RPCAPICommand("api_devdetails", "devdetails")]
        ),
        str(DataOptions.UPTIME): DataFunction(
            "get_uptime", [RPCAPICommand("api_summary", "summary")]
        ),
        str(DataOptions.CONFIG): DataFunction("get_config"),
    }
)


class BOSer(BaseMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip)
        # interfaces
        self.api = BOSMinerAPI(ip, api_ver)
        self.web = BOSerWebAPI(ip)

        # static data
        self.api_type = "BOSMiner"
        # data gathering locations
        self.data_locations = BOSER_DATA_LOC
        # autotuning/shutdown support
        self.supports_autotuning = True
        self.supports_shutdown = True

        # data storage
        self.api_ver = api_ver

    async def send_ssh_command(self, cmd: str) -> Optional[str]:
        result = None

        try:
            conn = await asyncio.wait_for(self._get_ssh_connection(), timeout=10)
        except (ConnectionError, asyncio.TimeoutError):
            return None

        # open an ssh connection
        async with conn:
            # 3 retries
            for i in range(3):
                try:
                    # run the command and get the result
                    result = await conn.run(cmd)
                    stderr = result.stderr
                    result = result.stdout

                    if len(stderr) > len(result):
                        result = stderr

                except Exception as e:
                    # if the command fails, log it
                    logging.warning(f"{self} command {cmd} error: {e}")

                    # on the 3rd retry, return None
                    if i == 3:
                        return
                    continue
        # return the result, either command output or None
        return result

    async def fault_light_on(self) -> bool:
        logging.debug(f"{self}: Sending fault_light on command.")
        ret = await self.send_ssh_command("miner fault_light on")
        logging.debug(f"{self}: fault_light on command completed.")
        if isinstance(ret, str):
            self.light = True
            return self.light
        return False

    async def fault_light_off(self) -> bool:
        logging.debug(f"{self}: Sending fault_light off command.")
        self.light = False
        ret = await self.send_ssh_command("miner fault_light off")
        logging.debug(f"{self}: fault_light off command completed.")
        if isinstance(ret, str):
            self.light = False
            return True
        return False

    async def restart_backend(self) -> bool:
        return await self.restart_bosminer()

    async def restart_bosminer(self) -> bool:
        logging.debug(f"{self}: Sending bosminer restart command.")
        ret = await self.send_ssh_command("/etc/init.d/bosminer restart")
        logging.debug(f"{self}: bosminer restart command completed.")
        if isinstance(ret, str):
            return True
        return False

    async def stop_mining(self) -> bool:
        try:
            data = await self.api.pause()
        except APIError:
            return False
        if data.get("PAUSE"):
            if data["PAUSE"][0]:
                return True
        return False

    async def resume_mining(self) -> bool:
        try:
            data = await self.api.resume()
        except APIError:
            return False
        if data.get("RESUME"):
            if data["RESUME"][0]:
                return True
        return False

    async def reboot(self) -> bool:
        logging.debug(f"{self}: Sending reboot command.")
        ret = await self.send_ssh_command("/sbin/reboot")
        logging.debug(f"{self}: Reboot command completed.")
        if isinstance(ret, str):
            return True
        return False

    async def get_config(self) -> MinerConfig:
        logging.debug(f"{self}: Getting config.")

        try:
            conn = await self._get_ssh_connection()
        except ConnectionError:
            conn = None

        if conn:
            async with conn:
                # good ol' BBB compatibility :/
                toml_data = toml.loads(
                    (await conn.run("cat /etc/bosminer.toml")).stdout
                )
            logging.debug(f"{self}: Converting config file.")
            cfg = MinerConfig.from_bosminer(toml_data)
            self.config = cfg
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        logging.debug(f"{self}: Sending config.")
        self.config = config

        if self.web.grpc is not None:
            try:
                await self._send_config_grpc(config, user_suffix)
                return
            except:
                pass
        await self._send_config_bosminer(config, user_suffix)

    async def _send_config_grpc(self, config: MinerConfig, user_suffix: str = None):
        raise NotImplementedError
        mining_mode = config.mining_mode

    async def _send_config_bosminer(self, config: MinerConfig, user_suffix: str = None):
        toml_conf = toml.dumps(
            {
                "format": {
                    "version": "1.2+",
                    "generator": "pyasic",
                    "model": f"{self.make.replace('Miner', 'miner')} {self.model.replace(' (BOS)', '').replace('j', 'J')}",
                    "timestamp": int(time.time()),
                },
                **config.as_bosminer(user_suffix=user_suffix),
            }
        )
        try:
            conn = await self._get_ssh_connection()
        except ConnectionError as e:
            raise APIError("SSH connection failed when sending config.") from e
        async with conn:
            # BBB check because bitmain suxx
            bbb_check = await conn.run(
                "if [ ! -f /etc/init.d/bosminer ]; then echo '1'; else echo '0'; fi;"
            )

            bbb = bbb_check.stdout.strip() == "1"

            if not bbb:
                await conn.run("/etc/init.d/bosminer stop")
                logging.debug(f"{self}: Opening SFTP connection.")
                async with conn.start_sftp_client() as sftp:
                    logging.debug(f"{self}: Opening config file.")
                    async with sftp.open("/etc/bosminer.toml", "w+") as file:
                        await file.write(toml_conf)
                logging.debug(f"{self}: Restarting BOSMiner")
                await conn.run("/etc/init.d/bosminer start")

            # I really hate BBB, please get rid of it if you have it
            else:
                await conn.run("/etc/init.d/S99bosminer stop")
                logging.debug(f"{self}: BBB sending config")
                await conn.run("echo '" + toml_conf + "' > /etc/bosminer.toml")
                logging.debug(f"{self}: BBB restarting bosminer.")
                await conn.run("/etc/init.d/S99bosminer start")

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            cfg = await self.get_config()
            if cfg is None:
                return False
            cfg.mining_mode = MiningModePowerTune(wattage)
            await self.send_config(cfg)
        except Exception as e:
            logging.warning(f"{self} set_power_limit: {e}")
            return False
        else:
            return True

    async def set_static_ip(
        self,
        ip: str,
        dns: str,
        gateway: str,
        subnet_mask: str = "255.255.255.0",
    ):
        cfg_data_lan = (
            "config interface 'lan'\n\toption type 'bridge'\n\toption ifname 'eth0'\n\toption proto 'static'\n\toption ipaddr '"
            + ip
            + "'\n\toption netmask '"
            + subnet_mask
            + "'\n\toption gateway '"
            + gateway
            + "'\n\toption dns '"
            + dns
            + "'"
        )
        data = await self.send_ssh_command("cat /etc/config/network")

        split_data = data.split("\n\n")
        for idx in range(len(split_data)):
            if "config interface 'lan'" in split_data[idx]:
                split_data[idx] = cfg_data_lan
        config = "\n\n".join(split_data)

        conn = await self._get_ssh_connection()

        async with conn:
            await conn.run("echo '" + config + "' > /etc/config/network")

    async def set_dhcp(self):
        cfg_data_lan = "config interface 'lan'\n\toption type 'bridge'\n\toption ifname 'eth0'\n\toption proto 'dhcp'"
        data = await self.send_ssh_command("cat /etc/config/network")

        split_data = data.split("\n\n")
        for idx in range(len(split_data)):
            if "config interface 'lan'" in split_data[idx]:
                split_data[idx] = cfg_data_lan
        config = "\n\n".join(split_data)

        conn = await self._get_ssh_connection()

        async with conn:
            await conn.run("echo '" + config + "' > /etc/config/network")

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(self, web_net_conf: Union[dict, list] = None) -> Optional[str]:
        if not web_net_conf:
            try:
                web_net_conf = await self.web.send_command(
                    "admin/network/iface_status/lan"
                )
            except APIError:
                pass

        if isinstance(web_net_conf, dict):
            if "admin/network/iface_status/lan" in web_net_conf.keys():
                web_net_conf = web_net_conf["admin/network/iface_status/lan"]

        if web_net_conf:
            try:
                return web_net_conf[0]["macaddr"]
            except LookupError:
                pass
        # could use ssh, but its slow and buggy
        # result = await self.send_ssh_command("cat /sys/class/net/eth0/address")
        # if result:
        #     return result.upper().strip()

    async def get_model(self) -> Optional[str]:
        if self.model is not None:
            return self.model + " (BOS)"
        return "? (BOS)"

    async def get_version(
        self, api_version: dict = None, graphql_version: dict = None
    ) -> Tuple[Optional[str], Optional[str]]:
        # check if version is cached
        miner_version = namedtuple("MinerVersion", "api_ver fw_ver")
        api_ver = await self.get_api_ver(api_version)
        fw_ver = await self.get_fw_ver(graphql_version)
        return miner_version(api_ver, fw_ver)

    async def get_api_ver(self, api_version: dict = None) -> Optional[str]:
        if not api_version:
            try:
                api_version = await self.api.version()
            except APIError:
                pass

        # Now get the API version
        if api_version:
            try:
                api_ver = api_version["VERSION"][0]["API"]
            except (KeyError, IndexError):
                api_ver = None
            self.api_ver = api_ver
            self.api.api_ver = self.api_ver

        return self.api_ver

    async def get_fw_ver(self, graphql_version: dict = None) -> Optional[str]:
        if not graphql_version:
            try:
                graphql_version = await self.web.send_command(
                    {"bos": {"info": {"version": {"full"}}}}
                )
            except APIError:
                pass

        fw_ver = None

        if graphql_version:
            try:
                fw_ver = graphql_version["data"]["bos"]["info"]["version"]["full"]
            except (KeyError, TypeError):
                pass

        if not fw_ver:
            # try version data file
            fw_ver = await self.send_ssh_command("cat /etc/bos_version")

        # if we get the version data, parse it
        if fw_ver is not None:
            ver = fw_ver.split("-")[5]
            if "." in ver:
                self.fw_ver = ver
                logging.debug(f"Found version for {self.ip}: {self.fw_ver}")

        return self.fw_ver

    async def get_hostname(self, graphql_hostname: dict = None) -> Union[str, None]:
        hostname = None

        if not graphql_hostname:
            try:
                graphql_hostname = await self.web.send_command({"bos": {"hostname"}})
            except APIError:
                pass

        if graphql_hostname:
            try:
                hostname = graphql_hostname["data"]["bos"]["hostname"]
                return hostname
            except (TypeError, KeyError):
                pass

        try:
            async with await self._get_ssh_connection() as conn:
                if conn is not None:
                    data = await conn.run("cat /proc/sys/kernel/hostname")
                    host = data.stdout.strip()
                    logging.debug(f"Found hostname for {self.ip}: {host}")
                    hostname = host
                else:
                    logging.warning(f"Failed to get hostname for miner: {self}")
        except Exception as e:
            logging.warning(f"Failed to get hostname for miner: {self}, {e}")
        return hostname

    async def get_hashrate(
        self, api_summary: dict = None, graphql_hashrate: dict = None
    ) -> Optional[float]:
        # get hr from graphql
        if not graphql_hashrate:
            try:
                graphql_hashrate = await self.web.send_command(
                    {"bosminer": {"info": {"workSolver": {"realHashrate": {"mhs1M"}}}}}
                )
            except APIError:
                pass

        if graphql_hashrate:
            try:
                return round(
                    float(
                        graphql_hashrate["data"]["bosminer"]["info"]["workSolver"][
                            "realHashrate"
                        ]["mhs1M"]
                        / 1000000
                    ),
                    2,
                )
            except (LookupError, ValueError, TypeError):
                pass

        # get hr from API
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

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
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if not graphql_boards and not (api_devs or api_temps or api_devdetails):
            try:
                graphql_boards = await self.web.send_command(
                    {
                        "bosminer": {
                            "info": {
                                "workSolver": {
                                    "childSolvers": {
                                        "name": None,
                                        "realHashrate": {"mhs1M"},
                                        "hwDetails": {"chips"},
                                        "temperatures": {"degreesC"},
                                    }
                                }
                            }
                        }
                    },
                )
            except APIError:
                pass

        if graphql_boards:
            try:
                boards = graphql_boards["data"]["bosminer"]["info"]["workSolver"][
                    "childSolvers"
                ]
            except (TypeError, LookupError):
                boards = None

            if boards:
                b_names = [int(b["name"]) for b in boards]
                offset = 0
                if 3 in b_names:
                    offset = 1
                elif 6 in b_names or 7 in b_names or 8 in b_names:
                    offset = 6
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
            try:
                d = await self.api.multicommand(*cmds)
            except APIError:
                d = {}
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
                offset = 6 if api_temps["TEMPS"][0]["ID"] in [6, 7, 8] else 1

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
                offset = 6 if api_devdetails["DEVDETAILS"][0]["ID"] in [6, 7, 8] else 1

                for board in api_devdetails["DEVDETAILS"]:
                    _id = board["ID"] - offset
                    chips = board["Chips"]
                    hashboards[_id].chips = chips
                    hashboards[_id].missing = False
            except (IndexError, KeyError):
                pass

        if api_devs:
            try:
                offset = 6 if api_devs["DEVS"][0]["ID"] in [6, 7, 8] else 1

                for board in api_devs["DEVS"]:
                    _id = board["ID"] - offset
                    hashrate = round(float(board["MHS 1m"] / 1000000), 2)
                    hashboards[_id].hashrate = hashrate
            except (IndexError, KeyError):
                pass

        return hashboards

    async def get_env_temp(self) -> Optional[float]:
        return None

    async def get_wattage(
        self, api_tunerstatus: dict = None, graphql_wattage: dict = None
    ) -> Optional[int]:
        if not graphql_wattage and not api_tunerstatus:
            try:
                graphql_wattage = await self.web.send_command(
                    {
                        "bosminer": {
                            "info": {"workSolver": {"power": {"approxConsumptionW"}}}
                        }
                    }
                )
            except APIError:
                pass
        if graphql_wattage is not None:
            try:
                return graphql_wattage["data"]["bosminer"]["info"]["workSolver"][
                    "power"
                ]["approxConsumptionW"]
            except (LookupError, TypeError):
                pass

        if not api_tunerstatus:
            try:
                api_tunerstatus = await self.api.tunerstatus()
            except APIError:
                pass

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
            try:
                graphql_wattage_limit = await self.web.send_command(
                    {"bosminer": {"info": {"workSolver": {"power": {"limitW"}}}}}
                )
            except APIError:
                pass

        if graphql_wattage_limit:
            try:
                return graphql_wattage_limit["data"]["bosminer"]["info"]["workSolver"][
                    "power"
                ]["limitW"]
            except (LookupError, TypeError):
                pass

        if not api_tunerstatus:
            try:
                api_tunerstatus = await self.api.tunerstatus()
            except APIError:
                pass

        if api_tunerstatus:
            try:
                return api_tunerstatus["TUNERSTATUS"][0]["PowerLimit"]
            except (KeyError, IndexError):
                pass

    async def get_fans(
        self, api_fans: dict = None, graphql_fans: dict = None
    ) -> List[Fan]:
        if not graphql_fans and not api_fans:
            try:
                graphql_fans = await self.web.send_command(
                    {"bosminer": {"info": {"fans": {"name", "rpm"}}}}
                )
            except APIError:
                pass
        if graphql_fans.get("data"):
            fans = []
            for n in range(self.fan_count):
                try:
                    fans.append(
                        Fan(
                            speed=graphql_fans["data"]["bosminer"]["info"]["fans"][n][
                                "rpm"
                            ]
                        )
                    )
                except (LookupError, TypeError):
                    pass
            return fans

        if not api_fans:
            try:
                api_fans = await self.api.fans()
            except APIError:
                pass

        if api_fans:
            fans = []
            for n in range(self.fan_count):
                try:
                    fans.append(Fan(api_fans["FANS"][n]["RPM"]))
                except (IndexError, KeyError):
                    pass
            return fans
        return [Fan() for _ in range(self.fan_count)]

    async def get_fan_psu(self) -> Optional[int]:
        return None

    async def get_errors(
        self, api_tunerstatus: dict = None, graphql_errors: dict = None
    ) -> List[MinerErrorData]:
        if not graphql_errors and not api_tunerstatus:
            try:
                graphql_errors = await self.web.send_command(
                    {
                        "bosminer": {
                            "info": {
                                "workSolver": {
                                    "childSolvers": {
                                        "name": None,
                                        "tuner": {"statusMessages"},
                                    }
                                }
                            }
                        }
                    }
                )
            except APIError:
                pass

        if graphql_errors:
            errors = []
            try:
                boards = graphql_errors["data"]["bosminer"]["info"]["workSolver"][
                    "childSolvers"
                ]
            except (LookupError, TypeError):
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
            try:
                api_tunerstatus = await self.api.tunerstatus()
            except APIError:
                pass

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
                    try:
                        graphql_fault_light = await self.web.send_command(
                            {"bos": {"faultLight"}}
                        )
                    except APIError:
                        pass
                else:
                    logging.info(
                        f"FW version {self.fw_ver} is too low for fault light info in graphql."
                    )
            else:
                # worth trying
                try:
                    graphql_fault_light = await self.web.send_command(
                        {"bos": {"faultLight"}}
                    )
                except APIError:
                    logging.debug(
                        "GraphQL fault light failed, likely due to version being too low (<=21.0.9)"
                    )
                if not graphql_fault_light:
                    # also a failure
                    logging.debug(
                        "GraphQL fault light failed, likely due to version being too low (<=21.0.9)"
                    )

        # get light through GraphQL
        if graphql_fault_light:
            try:
                self.light = graphql_fault_light["data"]["bos"]["faultLight"]
                return self.light
            except (TypeError, ValueError, LookupError):
                pass

        # get light via ssh if that fails (10x slower)
        try:
            data = (
                await self.send_ssh_command("cat /sys/class/leds/'Red LED'/delay_off")
            ).strip()
            self.light = False
            if data == "50":
                self.light = True
            return self.light
        except (TypeError, AttributeError):
            return self.light

    async def get_expected_hashrate(self, api_devs: dict = None) -> Optional[float]:
        if not api_devs:
            try:
                api_devs = await self.api.devs()
            except APIError:
                pass

        if api_devs:
            try:
                offset = 6 if api_devs["DEVS"][0]["ID"] in [6, 7, 8] else 0
                hr_list = []

                for board in api_devs["DEVS"]:
                    _id = board["ID"] - offset
                    expected_hashrate = round(float(board["Nominal MHS"] / 1000000), 2)
                    if expected_hashrate:
                        hr_list.append(expected_hashrate)
                if len(hr_list) == 0:
                    return 0
                else:
                    return round(
                        (sum(hr_list) / len(hr_list)) * self.expected_hashboards, 2
                    )
            except (IndexError, KeyError):
                pass

    async def is_mining(self, api_devdetails: dict = None) -> Optional[bool]:
        if not api_devdetails:
            try:
                api_devdetails = await self.api.send_command(
                    "devdetails", ignore_errors=True, allow_warning=False
                )
            except APIError:
                pass

        if api_devdetails:
            try:
                return not api_devdetails["STATUS"][0]["Msg"] == "Unavailable"
            except LookupError:
                pass

    async def get_uptime(self, api_summary: dict = None) -> Optional[int]:
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return int(api_summary["SUMMARY"][0]["Elapsed"])
            except LookupError:
                pass
