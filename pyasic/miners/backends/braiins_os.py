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
import base64
import logging
import time
from pathlib import Path
from typing import List, Optional, Union

import aiofiles
import toml

from pyasic.config import MinerConfig
from pyasic.config.mining import MiningModePowerTune
from pyasic.data import AlgoHashRate, Fan, HashBoard, HashUnit
from pyasic.data.error_codes import BraiinsOSError, MinerErrorData
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.errors import APIError
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.miners.device.firmware import BraiinsOSFirmware
from pyasic.rpc.bosminer import BOSMinerRPCAPI
from pyasic.ssh.braiins_os import BOSMinerSSH
from pyasic.web.braiins_os import BOSerWebAPI, BOSMinerWebAPI
from pyasic.web.braiins_os.proto.braiins.bos.v1 import SaveAction

BOSMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_net_conf", "admin/network/iface_status/lan")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_bos_info", "bos/info")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_devs", "devs")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [
                RPCAPICommand("rpc_temps", "temps"),
                RPCAPICommand("rpc_devdetails", "devdetails"),
                RPCAPICommand("rpc_devs", "devs"),
            ],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [RPCAPICommand("rpc_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [RPCAPICommand("rpc_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_fans", "fans")],
        ),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [RPCAPICommand("rpc_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [RPCAPICommand("rpc_devdetails", "devdetails")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
    }
)


class BOSMiner(BraiinsOSFirmware):
    """Handler for old versions of BraiinsOS+ (pre-gRPC)"""

    _rpc_cls = BOSMinerRPCAPI
    rpc: BOSMinerRPCAPI
    _web_cls = BOSMinerWebAPI
    web: BOSMinerWebAPI
    _ssh_cls = BOSMinerSSH
    ssh: BOSMinerSSH

    data_locations = BOSMINER_DATA_LOC

    supports_shutdown = True
    supports_autotuning = True

    async def fault_light_on(self) -> bool:
        ret = await self.ssh.fault_light_on()

        if isinstance(ret, str):
            self.light = True
            return self.light
        return False

    async def fault_light_off(self) -> bool:
        ret = await self.ssh.fault_light_off()

        if isinstance(ret, str):
            self.light = False
            return True
        return False

    async def restart_backend(self) -> bool:
        return await self.restart_bosminer()

    async def restart_bosminer(self) -> bool:
        ret = await self.ssh.restart_bosminer()

        if isinstance(ret, str):
            return True
        return False

    async def stop_mining(self) -> bool:
        try:
            data = await self.rpc.pause()
        except APIError:
            return False

        if data.get("PAUSE"):
            if data["PAUSE"][0]:
                return True
        return False

    async def resume_mining(self) -> bool:
        try:
            data = await self.rpc.resume()
        except APIError:
            return False

        if data.get("RESUME"):
            if data["RESUME"][0]:
                return True
        return False

    async def reboot(self) -> bool:
        ret = await self.ssh.reboot()

        if isinstance(ret, str):
            return True
        return False

    async def get_config(self) -> MinerConfig:
        raw_data = await self.ssh.get_config_file()

        try:
            toml_data = toml.loads(raw_data)
            cfg = MinerConfig.from_bosminer(toml_data)
            self.config = cfg
        except toml.TomlDecodeError as e:
            raise APIError("Failed to decode toml when getting config.") from e
        except TypeError as e:
            raise APIError("Failed to decode toml when getting config.") from e

        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config
        parsed_cfg = config.as_bosminer(user_suffix=user_suffix)

        toml_conf = toml.dumps(
            {
                "format": {
                    "version": "2.0",
                    "generator": "pyasic",
                    "model": f"{self.make.replace('Miner', 'miner')} {self.raw_model.replace('j', 'J')}",
                    "timestamp": int(time.time()),
                },
                **parsed_cfg,
            }
        )
        try:
            conn = await self.ssh._get_connection()
        except ConnectionError as e:
            raise APIError("SSH connection failed when sending config.") from e

        async with conn:
            await conn.run("/etc/init.d/bosminer stop")
            await conn.run("echo '" + toml_conf + "' > /etc/bosminer.toml")
            await conn.run("/etc/init.d/bosminer start")

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            cfg = await self.get_config()
            if cfg is None:
                return False
            cfg.mining_mode = MiningModePowerTune(wattage)
            await self.send_config(cfg)
        except APIError:
            raise
        except Exception as e:
            logging.warning(f"{self} - Failed to set power limit: {e}")
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
        data = await self.ssh.get_network_config()

        split_data = data.split("\n\n")
        for idx, val in enumerate(split_data):
            if "config interface 'lan'" in val:
                split_data[idx] = cfg_data_lan
        config = "\n\n".join(split_data)

        await self.ssh.send_command("echo '" + config + "' > /etc/config/network")

    async def set_dhcp(self):
        cfg_data_lan = "\n\t".join(
            [
                "config interface 'lan'",
                "option type 'bridge'",
                "option ifname 'eth0'",
                "option proto 'dhcp'",
            ]
        )
        data = await self.ssh.get_network_config()

        split_data = data.split("\n\n")
        for idx, val in enumerate(split_data):
            if "config interface 'lan'" in val:
                split_data[idx] = cfg_data_lan
        config = "\n\n".join(split_data)

        await self.ssh.send_command("echo '" + config + "' > /etc/config/network")

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(self, web_net_conf: Union[dict, list] = None) -> Optional[str]:
        if web_net_conf is None:
            try:
                web_net_conf = await self.web.get_net_conf()
            except APIError:
                pass

        if isinstance(web_net_conf, dict):
            if "admin/network/iface_status/lan" in web_net_conf.keys():
                web_net_conf = web_net_conf["admin/network/iface_status/lan"]

        if web_net_conf is not None:
            try:
                return web_net_conf[0]["macaddr"]
            except LookupError:
                pass
        # could use ssh, but its slow and buggy
        # result = await self.send_ssh_command("cat /sys/class/net/eth0/address")
        # if result:
        #     return result.upper().strip()

    async def _get_api_ver(self, rpc_version: dict = None) -> Optional[str]:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                pass

        # Now get the API version
        if rpc_version is not None:
            try:
                rpc_ver = rpc_version["VERSION"][0]["API"]
            except LookupError:
                rpc_ver = None
            self.api_ver = rpc_ver
            self.rpc.rpc_ver = self.api_ver

        return self.api_ver

    async def _get_fw_ver(self, web_bos_info: dict = None) -> Optional[str]:
        if web_bos_info is None:
            try:
                web_bos_info = await self.web.get_bos_info()
            except APIError:
                return None

        if isinstance(web_bos_info, dict):
            if "bos/info" in web_bos_info.keys():
                web_bos_info = web_bos_info["bos/info"]

        try:
            ver = web_bos_info["version"].split("-")[5]
            if "." in ver:
                self.fw_ver = ver
        except (LookupError, AttributeError):
            return None

        return self.fw_ver

    async def _get_hostname(self) -> Union[str, None]:
        try:
            hostname = (await self.ssh.get_hostname()).strip()
        except AttributeError:
            return None
        except Exception as e:
            logging.error(f"{self} - Getting hostname failed: {e}")
            return None
        return hostname

    async def _get_hashrate(self, rpc_summary: dict = None) -> Optional[AlgoHashRate]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return AlgoHashRate.SHA256(
                    rpc_summary["SUMMARY"][0]["MHS 1m"], HashUnit.SHA256.MH
                ).into(self.algo.unit.default)
            except (KeyError, IndexError, ValueError, TypeError):
                pass

    async def _get_hashboards(
        self,
        rpc_temps: dict = None,
        rpc_devdetails: dict = None,
        rpc_devs: dict = None,
    ) -> List[HashBoard]:
        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        cmds = []
        if rpc_temps is None:
            cmds.append("temps")
        if rpc_devdetails is None:
            cmds.append("devdetails")
        if rpc_devs is None:
            cmds.append("devs")
        if len(cmds) > 0:
            try:
                d = await self.rpc.multicommand(*cmds)
            except APIError:
                d = {}
            try:
                rpc_temps = d["temps"][0]
            except LookupError:
                rpc_temps = None
            try:
                rpc_devdetails = d["devdetails"][0]
            except (KeyError, IndexError):
                rpc_devdetails = None
            try:
                rpc_devs = d["devs"][0]
            except LookupError:
                rpc_devs = None
        if rpc_temps is not None:
            try:
                offset = 6 if rpc_temps["TEMPS"][0]["ID"] in [6, 7, 8] else 1

                for board in rpc_temps["TEMPS"]:
                    _id = board["ID"] - offset
                    chip_temp = round(board["Chip"])
                    board_temp = round(board["Board"])
                    hashboards[_id].chip_temp = chip_temp
                    hashboards[_id].temp = board_temp
            except (IndexError, KeyError, ValueError, TypeError):
                pass

        if rpc_devdetails is not None:
            try:
                offset = 6 if rpc_devdetails["DEVDETAILS"][0]["ID"] in [6, 7, 8] else 1

                for board in rpc_devdetails["DEVDETAILS"]:
                    _id = board["ID"] - offset
                    chips = board["Chips"]
                    hashboards[_id].chips = chips
                    hashboards[_id].missing = False
            except (IndexError, KeyError):
                pass

        if rpc_devs is not None:
            try:
                offset = 6 if rpc_devs["DEVS"][0]["ID"] in [6, 7, 8] else 1

                for board in rpc_devs["DEVS"]:
                    _id = board["ID"] - offset
                    hashboards[_id].hashrate = AlgoHashRate.SHA256(
                        board["MHS 1m"], HashUnit.SHA256.MH
                    ).into(self.algo.unit.default)
            except (IndexError, KeyError):
                pass

        return hashboards

    async def _get_wattage(self, rpc_tunerstatus: dict = None) -> Optional[int]:
        if rpc_tunerstatus is None:
            try:
                rpc_tunerstatus = await self.rpc.tunerstatus()
            except APIError:
                pass

        if rpc_tunerstatus is not None:
            try:
                return rpc_tunerstatus["TUNERSTATUS"][0][
                    "ApproximateMinerPowerConsumption"
                ]
            except LookupError:
                pass

    async def _get_wattage_limit(self, rpc_tunerstatus: dict = None) -> Optional[int]:
        if rpc_tunerstatus is None:
            try:
                rpc_tunerstatus = await self.rpc.tunerstatus()
            except APIError:
                pass

        if rpc_tunerstatus is not None:
            try:
                return rpc_tunerstatus["TUNERSTATUS"][0]["PowerLimit"]
            except LookupError:
                pass

    async def _get_fans(self, rpc_fans: dict = None) -> List[Fan]:
        if rpc_fans is None:
            try:
                rpc_fans = await self.rpc.fans()
            except APIError:
                pass

        if rpc_fans is not None:
            fans = []
            for n in range(self.expected_fans):
                try:
                    fans.append(Fan(rpc_fans["FANS"][n]["RPM"]))
                except (IndexError, KeyError):
                    pass
            return fans
        return [Fan() for _ in range(self.expected_fans)]

    async def _get_errors(self, rpc_tunerstatus: dict = None) -> List[MinerErrorData]:
        if rpc_tunerstatus is None:
            try:
                rpc_tunerstatus = await self.rpc.tunerstatus()
            except APIError:
                pass

        if rpc_tunerstatus is not None:
            errors = []
            try:
                chain_status = rpc_tunerstatus["TUNERSTATUS"][0]["TunerChainStatus"]
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
            data = (await self.ssh.get_led_status()).strip()
            self.light = False
            if data == "50":
                self.light = True
            return self.light
        except (TypeError, AttributeError):
            return self.light

    async def _get_expected_hashrate(
        self, rpc_devs: dict = None
    ) -> Optional[AlgoHashRate]:
        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                pass

        if rpc_devs is not None:
            try:
                hr_list = []

                for board in rpc_devs["DEVS"]:
                    expected_hashrate = round(float(board["Nominal MHS"] / 1000000), 2)
                    if expected_hashrate:
                        hr_list.append(expected_hashrate)

                if len(hr_list) == 0:
                    return AlgoHashRate.SHA256(0)
                else:
                    return AlgoHashRate.SHA256(
                        (sum(hr_list) / len(hr_list)) * self.expected_hashboards
                    )
            except (IndexError, KeyError):
                pass

    async def _is_mining(self, rpc_devdetails: dict = None) -> Optional[bool]:
        if rpc_devdetails is None:
            try:
                rpc_devdetails = await self.rpc.send_command(
                    "devdetails", ignore_errors=True, allow_warning=False
                )
            except APIError:
                pass

        if rpc_devdetails is not None:
            try:
                return not rpc_devdetails["STATUS"][0]["Msg"] == "Unavailable"
            except LookupError:
                pass

    async def _get_uptime(self, rpc_summary: dict = None) -> Optional[int]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return int(rpc_summary["SUMMARY"][0]["Elapsed"])
            except LookupError:
                pass

    async def _get_pools(self, rpc_pools: dict = None) -> List[PoolMetrics]:
        if rpc_pools is None:
            try:
                rpc_pools = await self.rpc.pools()
            except APIError:
                pass

        pools_data = []
        if rpc_pools is not None:
            try:
                pools = rpc_pools.get("POOLS", [])
                for pool_info in pools:
                    url = pool_info.get("URL")
                    pool_url = PoolUrl.from_str(url) if url else None
                    pool_data = PoolMetrics(
                        accepted=pool_info.get("Accepted"),
                        rejected=pool_info.get("Rejected"),
                        get_failures=pool_info.get("Get Failures"),
                        remote_failures=pool_info.get("Remote Failures"),
                        active=pool_info.get("Stratum Active"),
                        alive=pool_info.get("Status") == "Alive",
                        url=pool_url,
                        user=pool_info.get("User"),
                        index=pool_info.get("POOL"),
                    )
                    pools_data.append(pool_data)
            except LookupError:
                pass
        return pools_data

    async def upgrade_firmware(self, file: Path):
        """
        Upgrade the firmware of the BOSMiner device.

        Args:
            file (Path): The local file path of the firmware to be uploaded.

        Returns:
            str: Confirmation message after upgrading the firmware.
        """
        try:
            logging.info("Starting firmware upgrade process.")

            if not file:
                raise ValueError("File location must be provided for firmware upgrade.")

            # Read the firmware file contents
            async with aiofiles.open(file, "rb") as f:
                upgrade_contents = await f.read()

            # Encode the firmware contents in base64
            encoded_contents = base64.b64encode(upgrade_contents).decode("utf-8")

            # Upload the firmware file to the BOSMiner device
            logging.info(f"Uploading firmware file from {file} to the device.")
            await self.ssh.send_command(
                f"echo {encoded_contents} | base64 -d > /tmp/firmware.tar && sysupgrade /tmp/firmware.tar"
            )

            logging.info("Firmware upgrade process completed successfully.")
            return "Firmware upgrade completed successfully."
        except FileNotFoundError as e:
            logging.error(f"File not found during the firmware upgrade process: {e}")
            raise
        except ValueError as e:
            logging.error(
                f"Validation error occurred during the firmware upgrade process: {e}"
            )
            raise
        except OSError as e:
            logging.error(f"OS error occurred during the firmware upgrade process: {e}")
            raise
        except Exception as e:
            logging.error(
                f"An unexpected error occurred during the firmware upgrade process: {e}",
                exc_info=True,
            )
            raise


BOSER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [WebAPICommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [WebAPICommand("grpc_hashboards", "get_hashboards")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("grpc_miner_stats", "get_miner_stats")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [
                WebAPICommand(
                    "grpc_active_performance_mode", "get_active_performance_mode"
                )
            ],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("grpc_cooling_state", "get_cooling_state")],
        ),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [RPCAPICommand("rpc_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [WebAPICommand("grpc_locate_device_status", "get_locate_device_status")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [RPCAPICommand("rpc_devdetails", "devdetails")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
    }
)


class BOSer(BraiinsOSFirmware):
    """Handler for new versions of BraiinsOS+ (post-gRPC)"""

    _rpc_cls = BOSMinerRPCAPI
    web: BOSMinerRPCAPI
    _web_cls = BOSerWebAPI
    web: BOSerWebAPI

    data_locations = BOSER_DATA_LOC

    supports_autotuning = True
    supports_shutdown = True

    async def fault_light_on(self) -> bool:
        resp = await self.web.set_locate_device_status(True)
        if resp.get("enabled", False):
            return True
        return False

    async def fault_light_off(self) -> bool:
        resp = await self.web.set_locate_device_status(False)
        if resp == {}:
            return True
        return False

    async def restart_backend(self) -> bool:
        return await self.restart_boser()

    async def restart_boser(self) -> bool:
        await self.web.restart()
        return True

    async def stop_mining(self) -> bool:
        try:
            await self.web.pause_mining()
        except APIError:
            return False
        return True

    async def resume_mining(self) -> bool:
        try:
            await self.web.resume_mining()
        except APIError:
            return False
        return True

    async def reboot(self) -> bool:
        ret = await self.web.reboot()
        if ret == {}:
            return True
        return False

    async def get_config(self) -> MinerConfig:
        grpc_conf = await self.web.get_miner_configuration()

        return MinerConfig.from_boser(grpc_conf)

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        boser_cfg = config.as_boser(user_suffix=user_suffix)
        for key in boser_cfg:
            await self.web.send_command(key, message=boser_cfg[key])

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            result = await self.web.set_power_target(
                wattage, save_action=SaveAction.SAVE_ACTION_SAVE_AND_FORCE_APPLY
            )
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
        if grpc_miner_details is None:
            try:
                grpc_miner_details = await self.web.get_miner_details()
            except APIError:
                pass

        if grpc_miner_details is not None:
            try:
                return grpc_miner_details["macAddress"].upper()
            except (LookupError, TypeError):
                pass

    async def _get_api_ver(self, rpc_version: dict = None) -> Optional[str]:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                pass

        if rpc_version is not None:
            try:
                rpc_ver = rpc_version["VERSION"][0]["API"]
            except LookupError:
                rpc_ver = None
            self.api_ver = rpc_ver
            self.rpc.rpc_ver = self.api_ver

        return self.api_ver

    async def _get_fw_ver(self, grpc_miner_details: dict = None) -> Optional[str]:
        if grpc_miner_details is None:
            try:
                grpc_miner_details = await self.web.get_miner_details()
            except APIError:
                pass

        fw_ver = None

        if grpc_miner_details is not None:
            try:
                fw_ver = grpc_miner_details["bosVersion"]["current"]
            except (KeyError, TypeError):
                pass

        # if we get the version data, parse it
        if fw_ver is not None:
            ver = fw_ver.split("-")[5]
            if "." in ver:
                self.fw_ver = ver

        return self.fw_ver

    async def _get_hostname(self, grpc_miner_details: dict = None) -> Optional[str]:
        if grpc_miner_details is None:
            try:
                grpc_miner_details = await self.web.get_miner_details()
            except APIError:
                pass

        if grpc_miner_details is not None:
            try:
                return grpc_miner_details["hostname"]
            except LookupError:
                pass

    async def _get_hashrate(self, rpc_summary: dict = None) -> Optional[AlgoHashRate]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return AlgoHashRate.SHA256(
                    rpc_summary["SUMMARY"][0]["MHS 1m"], HashUnit.SHA256.MH
                ).into(self.algo.unit.default)
            except (KeyError, IndexError, ValueError, TypeError):
                pass

    async def _get_expected_hashrate(
        self, grpc_miner_details: dict = None
    ) -> Optional[AlgoHashRate]:
        if grpc_miner_details is None:
            try:
                grpc_miner_details = await self.web.get_miner_details()
            except APIError:
                pass

        if grpc_miner_details is not None:
            try:
                return AlgoHashRate.SHA256(
                    grpc_miner_details["stickerHashrate"]["gigahashPerSecond"],
                    HashUnit.SHA256.GH,
                ).into(self.algo.unit.default)
            except LookupError:
                pass

    async def _get_hashboards(self, grpc_hashboards: dict = None) -> List[HashBoard]:
        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if grpc_hashboards is None:
            try:
                grpc_hashboards = await self.web.get_hashboards()
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
                        hashboards[idx].hashrate = AlgoHashRate.SHA256(
                            board["stats"]["realHashrate"]["last5S"][
                                "gigahashPerSecond"
                            ],
                            HashUnit.SHA256.GH,
                        ).into(self.algo.unit.default)
                hashboards[idx].missing = False

        return hashboards

    async def _get_wattage(self, grpc_miner_stats: dict = None) -> Optional[int]:
        if grpc_miner_stats is None:
            try:
                grpc_miner_stats = self.web.get_miner_stats()
            except APIError:
                pass

        if grpc_miner_stats is not None:
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
                    await self.web.get_active_performance_mode()
                )
            except APIError:
                pass

        if grpc_active_performance_mode is not None:
            try:
                return grpc_active_performance_mode["tunerMode"]["powerTarget"][
                    "powerTarget"
                ]["watt"]
            except KeyError:
                pass

    async def _get_fans(self, grpc_cooling_state: dict = None) -> List[Fan]:
        if grpc_cooling_state is None:
            try:
                grpc_cooling_state = self.web.get_cooling_state()
            except APIError:
                pass

        if grpc_cooling_state is not None:
            fans = []
            for n in range(self.expected_fans):
                try:
                    fans.append(Fan(grpc_cooling_state["fans"][n]["rpm"]))
                except (IndexError, KeyError):
                    pass
            return fans
        return [Fan() for _ in range(self.expected_fans)]

    async def _get_errors(self, rpc_tunerstatus: dict = None) -> List[MinerErrorData]:
        if rpc_tunerstatus is None:
            try:
                rpc_tunerstatus = await self.rpc.tunerstatus()
            except APIError:
                pass

        if rpc_tunerstatus is not None:
            errors = []
            try:
                chain_status = rpc_tunerstatus["TUNERSTATUS"][0]["TunerChainStatus"]
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

        if grpc_locate_device_status is None:
            try:
                grpc_locate_device_status = await self.web.get_locate_device_status()
            except APIError:
                pass

        if grpc_locate_device_status is not None:
            if grpc_locate_device_status == {}:
                return False
            try:
                return grpc_locate_device_status["enabled"]
            except LookupError:
                pass

    async def _is_mining(self, rpc_devdetails: dict = None) -> Optional[bool]:
        if rpc_devdetails is None:
            try:
                rpc_devdetails = await self.rpc.send_command(
                    "devdetails", ignore_errors=True, allow_warning=False
                )
            except APIError:
                pass

        if rpc_devdetails is not None:
            try:
                return not rpc_devdetails["STATUS"][0]["Msg"] == "Unavailable"
            except LookupError:
                pass

    async def _get_uptime(self, rpc_summary: dict = None) -> Optional[int]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return int(rpc_summary["SUMMARY"][0]["Elapsed"])
            except LookupError:
                pass
