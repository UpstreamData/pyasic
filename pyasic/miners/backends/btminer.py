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

import logging
from pathlib import Path
from typing import List, Optional

import aiofiles

from pyasic.config import MinerConfig, MiningModeConfig
from pyasic.data import Fan, HashBoard
from pyasic.data.error_codes import MinerErrorData, WhatsminerError
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm import AlgoHashRate
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, RPCAPICommand
from pyasic.miners.device.firmware import StockFirmware
from pyasic.rpc.btminer import BTMinerRPCAPI


BTMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [
                RPCAPICommand("rpc_summary", "summary"),
                RPCAPICommand("rpc_get_miner_info", "get_miner_info"),
            ],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_get_version", "get_version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [
                RPCAPICommand("rpc_get_version", "get_version"),
                RPCAPICommand("rpc_summary", "summary"),
            ],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [RPCAPICommand("rpc_get_miner_info", "get_miner_info")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("rpc_devs", "devs")],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction(
            "_get_env_temp",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [
                RPCAPICommand("rpc_summary", "summary"),
                RPCAPICommand("rpc_get_psu", "get_psu"),
            ],
        ),
        str(DataOptions.FAN_PSU): DataFunction(
            "_get_fan_psu",
            [
                RPCAPICommand("rpc_summary", "summary"),
                RPCAPICommand("rpc_get_psu", "get_psu"),
            ],
        ),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [
                RPCAPICommand("rpc_get_error_code", "get_error_code"),
                RPCAPICommand("rpc_summary", "summary"),
            ],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [RPCAPICommand("rpc_get_miner_info", "get_miner_info")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [RPCAPICommand("rpc_status", "status")],
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


class BTMiner(StockFirmware):
    """Base handler for BTMiner based miners."""

    _rpc_cls = BTMinerRPCAPI
    rpc: BTMinerRPCAPI

    data_locations = BTMINER_DATA_LOC

    supports_shutdown = True
    supports_power_modes = True

    @staticmethod
    def _normalize_summary(rpc_summary: dict) -> dict:
        if "SUMMARY" not in rpc_summary:
            rpc_summary["SUMMARY"] = [rpc_summary["Msg"]]
        return rpc_summary

    async def _reset_rpc_pwd_to_admin(self, pwd: str):
        try:
            data = await self.rpc.update_pwd(pwd, "admin")
        except APIError:
            return False
        if data:
            if "Code" in data.keys():
                if data["Code"] == 131:
                    return True
        return False

    async def fault_light_off(self) -> bool:
        try:
            data = await self.rpc.set_led(auto=True)
        except APIError:
            return False
        if data:
            if "Code" in data.keys():
                if data["Code"] == 131:
                    self.light = False
                    return True
        return False

    async def fault_light_on(self) -> bool:
        try:
            data = await self.rpc.set_led(auto=False)
            await self.rpc.set_led(
                auto=False, color="green", start=0, period=1, duration=0
            )
        except APIError:
            return False
        if data:
            if "Code" in data.keys():
                if data["Code"] == 131:
                    self.light = True
                    return True
        return False

    async def reboot(self) -> bool:
        try:
            data = await self.rpc.reboot()
        except APIError:
            return False
        if data.get("Msg"):
            if data["Msg"] == "API command OK":
                return True
        return False

    async def restart_backend(self) -> bool:
        try:
            data = await self.rpc.restart()
        except APIError:
            return False
        if data.get("Msg"):
            if data["Msg"] == "API command OK":
                return True
        return False

    async def stop_mining(self) -> bool:
        try:
            data = await self.rpc.power_off(respbefore=True)
        except APIError:
            return False
        if data.get("Msg"):
            if data["Msg"] == "API command OK":
                return True
        return False

    async def resume_mining(self) -> bool:
        try:
            data = await self.rpc.power_on()
        except APIError:
            return False
        if data.get("Msg"):
            if data["Msg"] == "API command OK":
                return True
        return False

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config

        conf = config.as_wm(user_suffix=user_suffix)
        pools_conf = conf["pools"]

        try:
            await self.rpc.update_pools(**pools_conf)

            if conf["mode"] == "normal":
                await self.rpc.set_normal_power()
            elif conf["mode"] == "high":
                await self.rpc.set_high_power()
            elif conf["mode"] == "low":
                await self.rpc.set_low_power()
            elif conf["mode"] == "power_tuning":
                await self.rpc.adjust_power_limit(conf["power_tuning"]["wattage"])
        except APIError:
            # cannot update, no API access usually
            pass

    async def get_config(self) -> MinerConfig:
        pools = None
        summary = None
        status = None
        try:
            data = await self.rpc.multicommand("pools", "summary", "status")
            if "POOLS" in data:
                pools = {"POOLS": data["POOLS"]}
            elif "pools" in data:
                pools = data["pools"][0]
            else:
                raise LookupError("No pools data found")
            summary = data["summary"][0]
            status = data["status"][0]
        except APIError as e:
            logging.warning(e)
        except LookupError:
            pass

        if pools is not None:
            cfg = MinerConfig.from_api(pools)
        else:
            cfg = MinerConfig()
        is_mining = await self._is_mining(status)
        if not is_mining:
            cfg.mining_mode = MiningModeConfig.sleep()
            return cfg

        if summary is not None:
            mining_mode = None
            try:
                mining_mode = summary["SUMMARY"][0]["Power Mode"]
            except LookupError:
                pass

            if mining_mode == "High":
                cfg.mining_mode = MiningModeConfig.high()
                return cfg
            elif mining_mode == "Low":
                cfg.mining_mode = MiningModeConfig.low()
                return cfg
            try:
                power_lim = summary["SUMMARY"][0]["Power Limit"]
            except LookupError:
                power_lim = None

            if power_lim is None:
                cfg.mining_mode = MiningModeConfig.normal()
                return cfg

            cfg.mining_mode = MiningModeConfig.power_tuning(power=power_lim)
            self.config = cfg
            return self.config

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            await self.rpc.adjust_power_limit(wattage)
        except Exception as e:
            logging.warning(f"{self} set_power_limit: {e}")
            return False
        else:
            return True

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(
        self, rpc_summary: dict = None, rpc_get_miner_info: dict = None
    ) -> Optional[str]:
        if rpc_get_miner_info is None:
            try:
                rpc_get_miner_info = await self.rpc.get_miner_info()
            except APIError:
                pass

        if rpc_get_miner_info is not None:
            try:
                mac = rpc_get_miner_info["Msg"]["mac"]
                return str(mac).upper()
            except KeyError:
                pass

        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                rpc_summary = self._normalize_summary(rpc_summary)
                mac = rpc_summary["SUMMARY"][0]["MAC"]
                return str(mac).upper()
            except LookupError:
                pass

    async def _get_api_ver(self, rpc_get_version: dict = None) -> Optional[str]:
        if rpc_get_version is None:
            try:
                rpc_get_version = await self.rpc.get_version()
            except APIError:
                pass

        if rpc_get_version is not None:
            if "Code" in rpc_get_version.keys():
                if rpc_get_version["Code"] == 131:
                    try:
                        rpc_ver = rpc_get_version["Msg"]
                        if not isinstance(rpc_ver, str):
                            for ver_str in ("api_ver", "rpc_ver"):
                                if ver_str in rpc_ver:
                                    rpc_ver = rpc_ver[ver_str]
                            if not isinstance(rpc_ver, str):
                                raise KeyError("no valid key for rpc_ver")
                        self.api_ver = rpc_ver.replace("whatsminer v", "")
                    except (KeyError, TypeError):
                        pass
                    else:
                        self.rpc.rpc_ver = self.api_ver
                        return self.api_ver

        return self.api_ver

    async def _get_fw_ver(
        self, rpc_get_version: dict = None, rpc_summary: dict = None
    ) -> Optional[str]:
        if rpc_get_version is None:
            try:
                rpc_get_version = await self.rpc.get_version()
            except APIError:
                pass

        if rpc_get_version is not None:
            if "Code" in rpc_get_version.keys():
                if rpc_get_version["Code"] == 131:
                    try:
                        self.fw_ver = rpc_get_version["Msg"]["fw_ver"]
                    except (KeyError, TypeError):
                        pass
                    else:
                        return self.fw_ver

        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary:
            try:
                rpc_summary = self._normalize_summary(rpc_summary)
                self.fw_ver = rpc_summary["SUMMARY"][0]["Firmware Version"].replace(
                    "'", ""
                )
            except LookupError:
                pass

        return self.fw_ver

    async def _get_hostname(self, rpc_get_miner_info: dict = None) -> Optional[str]:
        hostname = None
        if rpc_get_miner_info is None:
            try:
                rpc_get_miner_info = await self.rpc.get_miner_info()
            except APIError:
                return None  # only one way to get this

        if rpc_get_miner_info is not None:
            try:
                hostname = rpc_get_miner_info["Msg"]["hostname"]
            except KeyError:
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
                rpc_summary = self._normalize_summary(rpc_summary)
                return self.algo.hashrate(
                    rate=float(rpc_summary["SUMMARY"][0]["MHS 1m"]),
                    unit=self.algo.unit.MH,
                ).into(self.algo.unit.default)
            except LookupError:
                pass

    async def _get_hashboards(self, rpc_devs: dict = None) -> List[HashBoard]:
        if self.expected_hashboards is None:
            return []

        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                pass

        if rpc_devs is not None:
            try:
                for board in rpc_devs["DEVS"]:
                    asc = board.get("ASC")
                    if asc is None:
                        asc = board["Slot"]
                    if len(hashboards) < asc + 1:
                        hashboards.append(
                            HashBoard(slot=asc, expected_chips=self.expected_chips)
                        )
                        self.expected_hashboards += 1
                    hashboards[asc].chip_temp = (
                        round(board.get("Chip Temp Avg"))
                        if "Chip Temp Avg" in board
                        else None
                    )
                    hashboards[asc].temp = round(board["Temperature"])
                    hashboards[asc].hashrate = self.algo.hashrate(
                        rate=float(board["MHS 1m"]), unit=self.algo.unit.MH
                    ).into(self.algo.unit.default)
                    hashboards[asc].chips = board["Effective Chips"]
                    hashboards[asc].serial_number = board["PCB SN"]
                    hashboards[asc].missing = False
            except LookupError:
                pass

        return hashboards

    async def _get_env_temp(self, rpc_summary: dict = None) -> Optional[float]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                rpc_summary = self._normalize_summary(rpc_summary)
                return rpc_summary["SUMMARY"][0]["Env Temp"]
            except LookupError:
                pass

    async def _get_wattage(self, rpc_summary: dict = None) -> Optional[int]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            if "SUMMARY" not in rpc_summary:
                rpc_summary["SUMMARY"] = [rpc_summary["Msg"]]
            try:
                rpc_summary = self._normalize_summary(rpc_summary)
                wattage = rpc_summary["SUMMARY"][0]["Power"]
                return wattage if not wattage == -1 else None
            except LookupError:
                pass

    async def _get_wattage_limit(self, rpc_summary: dict = None) -> Optional[int]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                rpc_summary = self._normalize_summary(rpc_summary)
                return rpc_summary["SUMMARY"][0]["Power Limit"]
            except LookupError:
                pass

    async def _get_fans(
        self, rpc_summary: dict = None, rpc_get_psu: dict = None
    ) -> List[Fan]:
        if self.expected_fans is None:
            return []

        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        fans = [Fan() for _ in range(self.expected_fans)]
        if rpc_summary is not None:
            try:
                rpc_summary = self._normalize_summary(rpc_summary)
                if self.expected_fans > 0:
                    fans = [
                        Fan(speed=rpc_summary["SUMMARY"][0].get("Fan Speed In", 0)),
                        Fan(speed=rpc_summary["SUMMARY"][0].get("Fan Speed Out", 0)),
                    ]
            except LookupError:
                pass

        return fans

    async def _get_fan_psu(
        self, rpc_summary: dict = None, rpc_get_psu: dict = None
    ) -> Optional[int]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                rpc_summary = self._normalize_summary(rpc_summary)
                return int(rpc_summary["SUMMARY"][0]["Power Fanspeed"])
            except LookupError:
                pass

        if rpc_get_psu is None:
            try:
                rpc_get_psu = await self.rpc.get_psu()
            except APIError:
                pass

        if rpc_get_psu is not None:
            try:
                return int(rpc_get_psu["Msg"]["fan_speed"])
            except (KeyError, TypeError):
                pass

    async def _get_errors(
        self, rpc_summary: dict = None, rpc_get_error_code: dict = None
    ) -> List[MinerErrorData]:
        errors = []
        if rpc_get_error_code is None and rpc_summary is None:
            try:
                rpc_get_error_code = await self.rpc.get_error_code()
            except APIError:
                pass

        if rpc_get_error_code is not None:
            try:
                for err in rpc_get_error_code["Msg"]["error_code"]:
                    if isinstance(err, dict):
                        for code in err:
                            errors.append(WhatsminerError(error_code=int(code)))
                    else:
                        errors.append(WhatsminerError(error_code=int(err)))
            except KeyError:
                pass

        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                rpc_summary = self._normalize_summary(rpc_summary)
                for i in range(rpc_summary["SUMMARY"][0]["Error Code Count"]):
                    err = rpc_summary["SUMMARY"][0].get(f"Error Code {i}")
                    if err:
                        errors.append(WhatsminerError(error_code=err))
            except (LookupError, ValueError, TypeError):
                pass
        return errors

    async def _get_expected_hashrate(
        self, rpc_summary: dict = None
    ) -> Optional[AlgoHashRate]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                rpc_summary = self._normalize_summary(rpc_summary)
                if "Factory GHS" in rpc_summary["SUMMARY"][0]:
                    expected_hashrate = rpc_summary["SUMMARY"][0]["Factory GHS"]
                else:
                    edevs = await self.rpc.edevs()
                    expected_hashrate = sum(dev["Factory GHS"] for dev in edevs["DEVS"])
                if expected_hashrate and expected_hashrate > 0:
                    return self.algo.hashrate(
                        rate=float(expected_hashrate), unit=self.algo.unit.GH
                    ).into(self.algo.unit.default)

            except LookupError:
                pass

    async def _get_fault_light(self, rpc_get_miner_info: dict = None) -> Optional[bool]:
        if rpc_get_miner_info is None:
            try:
                rpc_get_miner_info = await self.rpc.get_miner_info()
            except APIError:
                if not self.light:
                    self.light = False

        if rpc_get_miner_info is not None:
            try:
                self.light = not (rpc_get_miner_info["Msg"]["ledstat"] == "auto")
            except KeyError:
                pass

        return self.light if self.light else False

    async def set_static_ip(
        self,
        ip: str,
        dns: str,
        gateway: str,
        subnet_mask: str = "255.255.255.0",
        hostname: str = None,
    ):
        if not hostname:
            hostname = await self.get_hostname()
        await self.rpc.net_config(
            ip=ip, mask=subnet_mask, dns=dns, gate=gateway, host=hostname, dhcp=False
        )

    async def set_dhcp(self, hostname: str = None):
        if hostname:
            await self.set_hostname(hostname)
        await self.rpc.net_config()

    async def set_hostname(self, hostname: str):
        await self.rpc.set_hostname(hostname)

    async def _is_mining(self, rpc_status: dict = None) -> Optional[bool]:
        if rpc_status is None:
            try:
                rpc_status = await self.rpc.status()
            except APIError:
                pass

        if rpc_status is not None:
            try:
                if rpc_status["Msg"].get("btmineroff"):
                    try:
                        await self.rpc.devdetails()
                    except APIError:
                        return False
                    return True
                return True if rpc_status["Msg"]["mineroff"] == "false" else False
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
                rpc_summary = self._normalize_summary(rpc_summary)
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

    async def upgrade_firmware(self, file: Path) -> str:
        """
        Upgrade the firmware of the Whatsminer device.

        Args:
            file (Path): The local file path of the firmware to be uploaded.

        Returns:
            str: Confirmation message after upgrading the firmware.
        """
        try:
            logging.info("Starting firmware upgrade process for Whatsminer.")

            if not file:
                raise ValueError("File location must be provided for firmware upgrade.")

            # Read the firmware file contents
            async with aiofiles.open(file, "rb") as f:
                upgrade_contents = await f.read()

            result = await self.rpc.update_firmware(upgrade_contents)

            logging.info(
                "Firmware upgrade process completed successfully for Whatsminer."
            )
            return result
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
