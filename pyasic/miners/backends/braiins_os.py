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
    GRPCCommand,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.web.braiins_os import BOSerWebAPI, BOSMinerWebAPI

BOSMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_net_conf", "admin/network/iface_status/lan")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver", [RPCAPICommand("api_version", "version")]
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver", [WebAPICommand("web_bos_info", "bos/info")]
        ),
        str(DataOptions.HOSTNAME): DataFunction("_get_hostname"),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("api_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate", [RPCAPICommand("api_devs", "devs")]
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [
                RPCAPICommand("api_temps", "temps"),
                RPCAPICommand("api_devdetails", "devdetails"),
                RPCAPICommand("api_devs", "devs"),
            ],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction("_get_env_temp"),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [RPCAPICommand("api_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [RPCAPICommand("api_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("api_fans", "fans")],
        ),
        str(DataOptions.FAN_PSU): DataFunction("_get_fan_psu"),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [RPCAPICommand("api_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction("_get_fault_light"),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining", [RPCAPICommand("api_devdetails", "devdetails")]
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime", [RPCAPICommand("api_summary", "summary")]
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
        cfg_data_lan = "\n\t".join(
            [
                "config interface 'lan'",
                "option type 'bridge'",
                "option ifname 'eth0'",
                "option proto 'static'",
                f"option ipaddr '{ip}'",
                f"option netmask '{subnet_mask}'",
                f"option gateway '{gateway}'",
                f"option dns '{dns}'",
            ]
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
        cfg_data_lan = "\n\t".join(
            [
                "config interface 'lan'",
                "option type 'bridge'",
                "option ifname 'eth0'",
                "option proto 'dhcp'",
            ]
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

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(self, web_net_conf: Union[dict, list] = None) -> Optional[str]:
        if not web_net_conf:
            try:
                web_net_conf = await self.web.luci.get_net_conf()
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

    async def _get_api_ver(self, api_version: dict = None) -> Optional[str]:
        if not api_version:
            try:
                api_version = await self.api.version()
            except APIError:
                pass

        # Now get the API version
        if api_version:
            try:
                api_ver = api_version["VERSION"][0]["API"]
            except LookupError:
                api_ver = None
            self.api_ver = api_ver
            self.api.api_ver = self.api_ver

        return self.api_ver

    async def _get_fw_ver(self, web_bos_info: dict) -> Optional[str]:
        if web_bos_info is None:
            try:
                web_bos_info = await self.web.luci.get_bos_info()
            except APIError:
                return None

        if isinstance(web_bos_info, dict):
            if "bos/info" in web_bos_info.keys():
                web_bos_info = web_bos_info["bos/info"]

        try:
            ver = web_bos_info["version"].split("-")[5]
            if "." in ver:
                self.fw_ver = ver
                logging.debug(f"Found version for {self.ip}: {self.fw_ver}")
        except (LookupError, AttributeError):
            return None

        return self.fw_ver

    async def _get_hostname(self) -> Union[str, None]:
        try:
            hostname = (
                await self.send_ssh_command("cat /proc/sys/kernel/hostname")
            ).strip()
        except Exception as e:
            logging.error(f"BOSMiner get_hostname failed with error: {e}")
            return None
        return hostname

    async def _get_hashrate(self, api_summary: dict = None) -> Optional[float]:
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

    async def _get_hashboards(
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
            except LookupError:
                api_temps = None
            try:
                api_devdetails = d["devdetails"][0]
            except (KeyError, IndexError):
                api_devdetails = None
            try:
                api_devs = d["devs"][0]
            except LookupError:
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

    async def _get_env_temp(self) -> Optional[float]:
        return None

    async def _get_wattage(self, api_tunerstatus: dict = None) -> Optional[int]:
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
            except LookupError:
                pass

    async def _get_wattage_limit(self, api_tunerstatus: dict = None) -> Optional[int]:
        if not api_tunerstatus:
            try:
                api_tunerstatus = await self.api.tunerstatus()
            except APIError:
                pass

        if api_tunerstatus:
            try:
                return api_tunerstatus["TUNERSTATUS"][0]["PowerLimit"]
            except LookupError:
                pass

    async def _get_fans(self, api_fans: dict = None) -> List[Fan]:
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

    async def _get_fan_psu(self) -> Optional[int]:
        return None

    async def _get_errors(self, api_tunerstatus: dict = None) -> List[MinerErrorData]:
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

    async def _get_fault_light(self) -> bool:
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

    async def _get_expected_hashrate(self, api_devs: dict = None) -> Optional[float]:
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

    async def _is_mining(self, api_devdetails: dict = None) -> Optional[bool]:
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

    async def _get_uptime(self, api_summary: dict = None) -> Optional[int]:
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
            "_get_mac",
            [GRPCCommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver", [GRPCCommand("api_version", "get_api_version")]
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [GRPCCommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [GRPCCommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("api_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [GRPCCommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [GRPCCommand("grpc_hashboards", "get_hashboards")],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction("_get_env_temp"),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [GRPCCommand("grpc_miner_stats", "get_miner_stats")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [
                GRPCCommand(
                    "grpc_active_performance_mode", "get_active_performance_mode"
                )
            ],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [GRPCCommand("grpc_cooling_state", "get_cooling_state")],
        ),
        str(DataOptions.FAN_PSU): DataFunction("_get_fan_psu"),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [RPCAPICommand("api_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [GRPCCommand("grpc_locate_device_status", "get_locate_device_status")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining", [RPCAPICommand("api_devdetails", "devdetails")]
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime", [RPCAPICommand("api_summary", "summary")]
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

    async def fault_light_on(self) -> bool:
        resp = await self.web.grpc.set_locate_device_status(True)
        if resp.get("enabled", False):
            return True
        return False

    async def fault_light_off(self) -> bool:
        resp = await self.web.grpc.set_locate_device_status(False)
        if resp == {}:
            return True
        return False

    async def restart_backend(self) -> bool:
        return await self.restart_boser()

    async def restart_boser(self) -> bool:
        ret = await self.web.grpc.restart()
        return True

    async def stop_mining(self) -> bool:
        try:
            await self.web.grpc.pause_mining()
        except APIError:
            return False
        return True

    async def resume_mining(self) -> bool:
        try:
            await self.web.grpc.resume_mining()
        except APIError:
            return False
        return True

    async def reboot(self) -> bool:
        ret = await self.web.grpc.reboot()
        if ret == {}:
            return True
        return False

    async def get_config(self) -> MinerConfig:
        grpc_conf = await self.web.grpc.get_miner_configuration()

        return MinerConfig.from_boser(grpc_conf)

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        raise NotImplementedError
        logging.debug(f"{self}: Sending config.")
        self.config = config

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            result = await self.web.grpc.set_power_target(wattage)
        except APIError:
            return False

        try:
            if result["powerTarget"]["watt"] == wattage:
                return True
        except KeyError:
            pass
        return False

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(self, grpc_miner_details: dict = None) -> Optional[str]:
        if not grpc_miner_details:
            try:
                grpc_miner_details = await self.web.grpc.get_miner_details()
            except APIError:
                pass

        if grpc_miner_details:
            try:
                return grpc_miner_details["macAddress"].upper()
            except (LookupError, TypeError):
                pass

    async def _get_model(self) -> Optional[str]:
        if self.model is not None:
            return self.model + " (BOS)"
        return "? (BOS)"

    async def _get_api_ver(self, api_version: dict = None) -> Optional[str]:
        if not api_version:
            try:
                api_version = await self.api.version()
            except APIError:
                pass

        # Now get the API version
        if api_version:
            try:
                api_ver = api_version["VERSION"][0]["API"]
            except LookupError:
                api_ver = None
            self.api_ver = api_ver
            self.api.api_ver = self.api_ver

        return self.api_ver

    async def _get_fw_ver(self, grpc_miner_details: dict = None) -> Optional[str]:
        if not grpc_miner_details:
            try:
                grpc_miner_details = await self.web.grpc.get_miner_details()
            except APIError:
                pass

        fw_ver = None

        if grpc_miner_details:
            try:
                fw_ver = grpc_miner_details["bosVersion"]["current"]
            except (KeyError, TypeError):
                pass

        # if we get the version data, parse it
        if fw_ver is not None:
            ver = fw_ver.split("-")[5]
            if "." in ver:
                self.fw_ver = ver
                logging.debug(f"Found version for {self.ip}: {self.fw_ver}")

        return self.fw_ver

    async def _get_hostname(self, grpc_miner_details: dict = None) -> Union[str, None]:
        if not grpc_miner_details:
            try:
                grpc_miner_details = await self.web.grpc.get_miner_details()
            except APIError:
                pass

        if grpc_miner_details:
            try:
                return grpc_miner_details["hostname"]
            except LookupError:
                pass

    async def _get_hashrate(self, api_summary: dict = None) -> Optional[float]:
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

    async def _get_expected_hashrate(
        self, grpc_miner_details: dict = None
    ) -> Optional[float]:
        if not grpc_miner_details:
            try:
                grpc_miner_details = await self.web.grpc.get_miner_details()
            except APIError:
                pass

        if grpc_miner_details:
            try:
                return grpc_miner_details["stickerHashrate"]["gigahashPerSecond"] / 1000
            except LookupError:
                pass

    async def _get_hashboards(self, grpc_hashboards: dict = None):
        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if grpc_hashboards is None:
            try:
                grpc_hashboards = await self.web.grpc.get_hashboards()
            except APIError:
                pass

        if grpc_hashboards is not None:
            for board in grpc_hashboards["hashboards"]:
                idx = int(board["id"]) - 1
                if board.get("chipsCount") is not None:
                    hashboards[idx].chips = board["chipsCount"]
                if board.get("boardTemp") is not None:
                    hashboards[idx].temp = board["boardTemp"]["degreeC"]
                if board.get("highestChipTemp") is not None:
                    hashboards[idx].chip_temp = board["highestChipTemp"]["temperature"][
                        "degreeC"
                    ]
                if board.get("stats") is not None:
                    if not board["stats"]["realHashrate"]["last5S"] == {}:
                        hashboards[idx].hashrate = round(
                            board["stats"]["realHashrate"]["last5S"][
                                "gigahashPerSecond"
                            ]
                            / 1000,
                            2,
                        )
                hashboards[idx].missing = False

        return hashboards

    async def _get_env_temp(self) -> Optional[float]:
        return None

    async def _get_wattage(self, grpc_miner_stats: dict = None) -> Optional[int]:
        if grpc_miner_stats is None:
            try:
                grpc_miner_stats = self.web.grpc.get_miner_stats()
            except APIError:
                pass

        if grpc_miner_stats:
            try:
                return grpc_miner_stats["powerStats"]["approximatedConsumption"]["watt"]
            except KeyError:
                pass

    async def _get_wattage_limit(
        self, grpc_active_performance_mode: dict = None
    ) -> Optional[int]:
        if grpc_active_performance_mode is None:
            try:
                grpc_active_performance_mode = (
                    self.web.grpc.get_active_performance_mode()
                )
            except APIError:
                pass

        if grpc_active_performance_mode:
            try:
                return grpc_active_performance_mode["tunerMode"]["powerTarget"][
                    "powerTarget"
                ]["watt"]
            except KeyError:
                pass

    async def _get_fans(self, grpc_cooling_state: dict = None) -> List[Fan]:
        if grpc_cooling_state is None:
            try:
                grpc_cooling_state = self.web.grpc.get_cooling_state()
            except APIError:
                pass

        if grpc_cooling_state:
            fans = []
            for n in range(self.fan_count):
                try:
                    fans.append(Fan(grpc_cooling_state["fans"][n]["rpm"]))
                except (IndexError, KeyError):
                    pass
            return fans
        return [Fan() for _ in range(self.fan_count)]

    async def _get_fan_psu(self) -> Optional[int]:
        return None

    async def _get_errors(self, api_tunerstatus: dict = None) -> List[MinerErrorData]:
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
            except LookupError:
                pass

    async def _get_fault_light(self, grpc_locate_device_status: dict = None) -> bool:
        if self.light is not None:
            return self.light

        if not grpc_locate_device_status:
            try:
                grpc_locate_device_status = (
                    await self.web.grpc.get_locate_device_status()
                )
            except APIError:
                pass

        if grpc_locate_device_status is not None:
            if grpc_locate_device_status == {}:
                return False
            try:
                return grpc_locate_device_status["enabled"]
            except LookupError:
                pass

    async def _is_mining(self, api_devdetails: dict = None) -> Optional[bool]:
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

    async def _get_uptime(self, api_summary: dict = None) -> Optional[int]:
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
