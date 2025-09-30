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
from typing import Any

import aiofiles
import semver
from pydantic import BaseModel, Field, ValidationError

from pyasic.config import MinerConfig
from pyasic.config.mining import MiningModeConfig
from pyasic.data.boards import HashBoard
from pyasic.data.error_codes import MinerErrorData, WhatsminerError
from pyasic.data.fans import Fan
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, RPCAPICommand
from pyasic.miners.device.firmware import StockFirmware
from pyasic.rpc.btminer import (
    BTMinerRPCAPI,
    BTMinerV3DeviceInfoMsg,
    BTMinerV3EdevItem,
    BTMinerV3Pool,
    BTMinerV3RPCAPI,
    BTMinerV3Summary,
)


class BTMinerMsgInfo(BaseModel):
    hostname: str | None = None
    mac: str | None = None
    model: str | None = None
    nettype: str | None = None

    class Config:
        extra = "allow"


class BTMinerGetMinerInfoResponse(BaseModel):
    msg: BTMinerMsgInfo = Field(alias="Msg")

    class Config:
        populate_by_name = True
        extra = "allow"


class BTMinerGetVersionResponse(BaseModel):
    code: int = Field(alias="Code")
    msg: dict[str, Any] | str = Field(alias="Msg")

    class Config:
        populate_by_name = True
        extra = "allow"


class BTMinerSummaryItem(BaseModel):
    mac: str | None = Field(None, alias="MAC")
    firmware_version: str | None = Field(None, alias="Firmware Version")
    mhs_1m: float | None = Field(None, alias="MHS 1m")
    env_temp: float | None = Field(None, alias="Env Temp")
    power: int | None = Field(None, alias="Power")
    power_limit: int | None = Field(None, alias="Power Limit")
    fan_speed_in: int | None = Field(None, alias="Fan Speed In")
    fan_speed_out: int | None = Field(None, alias="Fan Speed Out")
    power_fanspeed: int | None = Field(None, alias="Power Fanspeed")
    factory_ghs: float | None = Field(None, alias="Factory GHS")
    error_code_count: int = Field(0, alias="Error Code Count")
    elapsed: int | None = Field(None, alias="Elapsed")
    power_mode: str | None = Field(None, alias="Power Mode")

    class Config:
        populate_by_name = True
        extra = "allow"


class BTMinerSummaryResponse(BaseModel):
    summary: list[BTMinerSummaryItem] = Field([], alias="SUMMARY")

    class Config:
        populate_by_name = True
        extra = "allow"


class BTMinerDevItem(BaseModel):
    asc: int | None = Field(None, alias="ASC")
    slot: int | None = Field(None, alias="Slot")
    chip_temp_avg: float | None = Field(None, alias="Chip Temp Avg")
    temperature: float | None = Field(None, alias="Temperature")
    mhs_1m: float | None = Field(None, alias="MHS 1m")
    effective_chips: int | None = Field(None, alias="Effective Chips")
    pcb_sn: str | None = Field(None, alias="PCB SN")

    class Config:
        populate_by_name = True
        extra = "allow"


class BTMinerDevsResponse(BaseModel):
    devs: list[BTMinerDevItem] = Field([], alias="DEVS")

    class Config:
        populate_by_name = True
        extra = "allow"


class BTMinerStatusMsg(BaseModel):
    btmineroff: bool | None = None
    mineroff: str | None = None

    class Config:
        extra = "allow"


class BTMinerStatusResponse(BaseModel):
    msg: BTMinerStatusMsg = Field(alias="Msg")

    class Config:
        populate_by_name = True
        extra = "allow"


class BTMinerGetPSUResponse(BaseModel):
    msg: dict[str, Any] = Field(alias="Msg")

    class Config:
        populate_by_name = True
        extra = "allow"


class BTMinerGetErrorCodeResponse(BaseModel):
    msg: dict[str, Any] = Field(alias="Msg")

    class Config:
        populate_by_name = True
        extra = "allow"


class BTMinerPoolItem(BaseModel):
    pool: int | None = Field(None, alias="POOL")
    url: str | None = Field(None, alias="URL")
    user: str | None = Field(None, alias="User")
    accepted: int | None = Field(None, alias="Accepted")
    rejected: int | None = Field(None, alias="Rejected")
    get_failures: int | None = Field(None, alias="Get Failures")
    remote_failures: int | None = Field(None, alias="Remote Failures")
    stratum_active: bool | None = Field(None, alias="Stratum Active")
    status: str | None = Field(None, alias="Status")

    class Config:
        populate_by_name = True
        extra = "allow"


class BTMinerPoolsResponse(BaseModel):
    pools: list[BTMinerPoolItem] = Field([], alias="POOLS")

    class Config:
        populate_by_name = True
        extra = "allow"


class BTMinerV3CommandResponse(BaseModel):
    code: int | None = None
    msg: str | None = None

    class Config:
        extra = "allow"


class BTMiner(StockFirmware):
    def __new__(cls, ip: str, version: str | None = None) -> Any:
        bases = cls.__bases__
        bases = bases[1:]

        def get_new(v: str | None) -> type[BTMinerV2] | type[BTMinerV3]:
            if v is None:
                return BTMinerV2
            try:
                semantic = semver.Version(
                    major=int(v[0:4]),
                    minor=int(v[4:6]),
                    patch=int(v[6:8]),
                )
            except ValueError:
                return BTMinerV2
            if semantic > semver.Version(major=2024, minor=11, patch=0):
                return BTMinerV3
            return BTMinerV2

        inject = get_new(version)

        bases = (inject,) + bases

        new_class = type(cls.__name__, bases, {})
        return new_class(ip=ip, version=version)


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


class BTMinerV2(StockFirmware):
    """Base handler for BTMiner based miners."""

    _rpc_cls = BTMinerRPCAPI
    rpc: BTMinerRPCAPI

    data_locations = BTMINER_DATA_LOC

    supports_shutdown = True
    supports_power_modes = True

    async def _reset_rpc_pwd_to_admin(self, pwd: str) -> bool:
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

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
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
            pools = data["pools"][0]
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
            try:
                response = BTMinerSummaryResponse.model_validate(summary)
                if response.summary:
                    mining_mode = response.summary[0].power_mode
                    power_lim = response.summary[0].power_limit
                else:
                    mining_mode = None
                    power_lim = None
            except ValidationError:
                mining_mode = None
                power_lim = None

            if mining_mode == "High":
                cfg.mining_mode = MiningModeConfig.high()
                return cfg
            elif mining_mode == "Low":
                cfg.mining_mode = MiningModeConfig.low()
                return cfg

            if power_lim is None:
                cfg.mining_mode = MiningModeConfig.normal()
                return cfg

            cfg.mining_mode = MiningModeConfig.power_tuning(power=power_lim)
            self.config = cfg
            return self.config

        cfg.mining_mode = MiningModeConfig.normal()
        return cfg

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            await self.rpc.adjust_power_limit(wattage)
        except Exception as e:
            logging.warning(f"{self} set_power_limit: {e}")
            return False
        else:
            return True
        return False

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(
        self,
        rpc_summary: dict[str, Any] | None = None,
        rpc_get_miner_info: dict[str, Any] | None = None,
    ) -> str | None:
        if rpc_get_miner_info is None:
            try:
                rpc_get_miner_info = await self.rpc.get_miner_info()
            except APIError:
                pass

        if rpc_get_miner_info is not None:
            try:
                response = BTMinerGetMinerInfoResponse.model_validate(
                    rpc_get_miner_info
                )
                if response.msg.mac:
                    return str(response.msg.mac).upper()
            except ValidationError:
                pass

        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                summary_response = BTMinerSummaryResponse.model_validate(rpc_summary)
                if summary_response.summary and summary_response.summary[0].mac:
                    return str(summary_response.summary[0].mac).upper()
            except ValidationError:
                pass

        return None

    async def _get_api_ver(
        self, rpc_get_version: dict[str, Any] | None = None
    ) -> str | None:
        if rpc_get_version is None:
            try:
                rpc_get_version = await self.rpc.get_version()
            except APIError:
                pass

        if rpc_get_version is not None:
            try:
                response = BTMinerGetVersionResponse.model_validate(rpc_get_version)
                if response.code == 131:
                    if isinstance(response.msg, str):
                        self.api_ver = response.msg.replace("whatsminer v", "")
                    elif isinstance(response.msg, dict) and "rpc_ver" in response.msg:
                        self.api_ver = response.msg["rpc_ver"].replace(
                            "whatsminer v", ""
                        )
                    return self.api_ver
            except ValidationError:
                pass

        return self.api_ver

    async def _get_fw_ver(
        self,
        rpc_get_version: dict[str, Any] | None = None,
        rpc_summary: dict[str, Any] | None = None,
    ) -> str | None:
        if rpc_get_version is None:
            try:
                rpc_get_version = await self.rpc.get_version()
            except APIError:
                pass

        if rpc_get_version is not None:
            try:
                response = BTMinerGetVersionResponse.model_validate(rpc_get_version)
                if (
                    response.code == 131
                    and isinstance(response.msg, dict)
                    and "fw_ver" in response.msg
                ):
                    self.fw_ver = response.msg["fw_ver"]
                    return self.fw_ver
            except ValidationError:
                pass

        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary:
            try:
                summary_response = BTMinerSummaryResponse.model_validate(rpc_summary)
                if (
                    summary_response.summary
                    and summary_response.summary[0].firmware_version
                ):
                    self.fw_ver = summary_response.summary[0].firmware_version.replace(
                        "'", ""
                    )
                    return self.fw_ver
            except ValidationError:
                pass

        return self.fw_ver

    async def _get_hostname(
        self, rpc_get_miner_info: dict[str, Any] | None = None
    ) -> str | None:
        if rpc_get_miner_info is None:
            try:
                rpc_get_miner_info = await self.rpc.get_miner_info()
            except APIError:
                return None  # only one way to get this

        if rpc_get_miner_info is not None:
            try:
                response = BTMinerGetMinerInfoResponse.model_validate(
                    rpc_get_miner_info
                )
                return response.msg.hostname
            except ValidationError:
                pass
        return None

    async def _get_hashrate(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return self.algo.hashrate(
                    rate=float(rpc_summary["SUMMARY"][0]["MHS 1m"]),
                    unit=self.algo.unit.MH,  # type: ignore[attr-defined]
                ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except LookupError:
                pass
        return None

    async def _get_hashboards(
        self, rpc_devs: dict[str, Any] | None = None
    ) -> list[HashBoard]:
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
                    hashboards[asc].chip_temp = round(board["Chip Temp Avg"])
                    hashboards[asc].temp = round(board["Temperature"])
                    hashboards[asc].hashrate = self.algo.hashrate(
                        rate=float(board["MHS 1m"]),
                        unit=self.algo.unit.MH,  # type: ignore[attr-defined]
                    ).into(
                        self.algo.unit.default  # type: ignore[attr-defined]
                    )
                    hashboards[asc].chips = board["Effective Chips"]
                    hashboards[asc].serial_number = board["PCB SN"]
                    hashboards[asc].missing = False
            except LookupError:
                pass

        return hashboards

    async def _get_env_temp(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> float | None:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return float(rpc_summary["SUMMARY"][0]["Env Temp"])
            except LookupError:
                pass
        return None

    async def _get_wattage(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> int | None:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                wattage = rpc_summary["SUMMARY"][0]["Power"]
                return wattage if not wattage == -1 else None
            except LookupError:
                pass
        return None

    async def _get_wattage_limit(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> int | None:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return int(rpc_summary["SUMMARY"][0]["Power Limit"])
            except LookupError:
                pass
        return None

    async def _get_fans(
        self,
        rpc_summary: dict[str, Any] | None = None,
        rpc_get_psu: dict[str, Any] | None = None,
    ) -> list[Fan]:
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
                if self.expected_fans > 0:
                    fans = [
                        Fan(speed=rpc_summary["SUMMARY"][0].get("Fan Speed In", 0)),
                        Fan(speed=rpc_summary["SUMMARY"][0].get("Fan Speed Out", 0)),
                    ]
            except LookupError:
                pass

        return fans

    async def _get_fan_psu(
        self,
        rpc_summary: dict[str, Any] | None = None,
        rpc_get_psu: dict[str, Any] | None = None,
    ) -> int | None:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
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
        return None

    async def _get_errors(
        self,
        rpc_summary: dict[str, Any] | None = None,
        rpc_get_error_code: dict[str, Any] | None = None,
    ) -> list[MinerErrorData]:
        errors = []
        if rpc_get_error_code is None and rpc_summary is None:
            try:
                rpc_get_error_code = await self.rpc.get_error_code()
            except APIError:
                pass

        if rpc_get_error_code is not None:
            try:
                error_response = BTMinerGetErrorCodeResponse.model_validate(
                    rpc_get_error_code
                )
                if "error_code" in error_response.msg:
                    for err in error_response.msg["error_code"]:
                        if isinstance(err, dict):
                            for code in err:
                                errors.append(WhatsminerError(error_code=int(code)))
                        else:
                            errors.append(WhatsminerError(error_code=int(err)))
            except (ValidationError, ValueError, TypeError) as e:
                if isinstance(e, ValidationError):
                    logging.warning(f"{self} - Failed to parse error codes: {e}")

        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                response = BTMinerSummaryResponse.model_validate(rpc_summary)
                if response.summary:
                    for i in range(response.summary[0].error_code_count):
                        raw_data = rpc_summary["SUMMARY"][0]
                        err = raw_data.get(f"Error Code {i}")
                        if err:
                            errors.append(WhatsminerError(error_code=err))
            except (ValidationError, ValueError, TypeError) as e:
                if isinstance(e, ValidationError):
                    logging.warning(f"{self} - Failed to parse summary for errors: {e}")
        return errors  # type: ignore[return-value]

    async def _get_expected_hashrate(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                expected_hashrate = rpc_summary["SUMMARY"][0]["Factory GHS"]
                if expected_hashrate:
                    return self.algo.hashrate(
                        rate=float(expected_hashrate),
                        unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                    ).into(self.algo.unit.default)  # type: ignore[attr-defined]

            except LookupError:
                pass
        return None

    async def _get_fault_light(
        self, rpc_get_miner_info: dict[str, Any] | None = None
    ) -> bool | None:
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
        hostname: str | None = None,
    ) -> None:
        if not hostname:
            hostname = await self.get_hostname()
        if hostname is None:
            hostname = str(self.ip)
        await self.rpc.net_config(
            ip=ip, mask=subnet_mask, dns=dns, gate=gateway, host=hostname, dhcp=False
        )

    async def set_dhcp(self, hostname: str | None = None) -> None:
        if hostname:
            await self.set_hostname(hostname)
        await self.rpc.net_config()

    async def set_hostname(self, hostname: str) -> None:
        await self.rpc.set_hostname(hostname)

    async def _is_mining(self, rpc_status: dict[str, Any] | None = None) -> bool | None:
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
        return False

    async def _get_uptime(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> int | None:
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
        return None

    async def _get_pools(
        self, rpc_pools: dict[str, Any] | None = None
    ) -> list[PoolMetrics]:
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

    async def upgrade_firmware(
        self,
        *,
        file: str | None = None,
        url: str | None = None,
        version: str | None = None,
        keep_settings: bool = True,
    ) -> bool:
        """
        Upgrade the firmware of the Whatsminer device.

        Args:
            file: The local file path of the firmware to be uploaded.
            url: URL to download firmware from (not supported).
            version: Specific version to upgrade to (not supported).
            keep_settings: Whether to keep settings after upgrade.

        Returns:
            bool: True if firmware upgrade was successful.
        """
        try:
            logging.info("Starting firmware upgrade process for Whatsminer.")

            if not file:
                raise ValueError("File location must be provided for firmware upgrade.")

            # Read the firmware file contents
            async with aiofiles.open(file, "rb") as f:
                upgrade_contents = await f.read()

            await self.rpc.update_firmware(upgrade_contents)

            logging.info(
                "Firmware upgrade process completed successfully for Whatsminer."
            )
            return True
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


BTMINERV3_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac", [RPCAPICommand("rpc_get_device_info", "get.device.info")]
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_version",
            [RPCAPICommand("rpc_get_device_info", "get.device.info")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_firmware_version",
            [RPCAPICommand("rpc_get_device_info", "get.device.info")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname", [RPCAPICommand("rpc_get_device_info", "get.device.info")]
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_light_flashing",
            [RPCAPICommand("rpc_get_device_info", "get.device.info")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [RPCAPICommand("rpc_get_device_info", "get.device.info")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_get_miner_status_summary", "get.miner.status:summary")],
        ),
        str(DataOptions.FAN_PSU): DataFunction(
            "_get_psu_fans", [RPCAPICommand("rpc_get_device_info", "get.device.info")]
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [
                RPCAPICommand("rpc_get_device_info", "get.device.info"),
                RPCAPICommand(
                    "rpc_get_miner_status_edevs",
                    "get.miner.status:edevs",
                ),
            ],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_get_miner_status_pools", "get.miner.status:pools")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_get_miner_status_summary", "get.miner.status:summary")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [RPCAPICommand("rpc_get_miner_status_summary", "get.miner.status:summary")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_get_miner_status_summary", "get.miner.status:summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_get_miner_status_summary", "get.miner.status:summary")],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction(
            "_get_env_temp",
            [RPCAPICommand("rpc_get_miner_status_summary", "get.miner.status:summary")],
        ),
    }
)


class BTMinerV3(StockFirmware):
    _rpc_cls = BTMinerV3RPCAPI
    rpc: BTMinerV3RPCAPI

    data_locations = BTMINERV3_DATA_LOC

    supports_shutdown = True
    supports_autotuning = True
    supports_power_modes = True

    async def get_config(self) -> MinerConfig:
        pools = None
        settings = None
        device_info = None
        try:
            pools_list = await self.rpc.get_miner_status_pools()
            pools = {
                "msg": {
                    "pools": [pool.model_dump(by_alias=True) for pool in pools_list]
                }
            }
            settings_msg = await self.rpc.get_miner_setting()
            settings = settings_msg.model_dump(by_alias=True)
            device_info_msg = await self.rpc.get_device_info()
            device_info = device_info_msg.model_dump(by_alias=True)
        except APIError as e:
            logging.warning(e)
        except LookupError:
            pass

        if pools is not None and settings is not None and device_info is not None:
            self.config = MinerConfig.from_btminer_v3(
                rpc_pools=pools, rpc_settings=settings, rpc_device_info=device_info
            )
        else:
            self.config = MinerConfig()

        return self.config

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        self.config = config

        conf = config.as_btminer_v3(user_suffix=user_suffix)

        await asyncio.gather(
            *[self.rpc.send_command(k, parameters=v) for k, v in conf.values()]
        )

    async def fault_light_off(self) -> bool:
        try:
            await self.rpc.set_system_led()
            self.light = False
            return True
        except APIError:
            return False

    async def fault_light_on(self) -> bool:
        try:
            await self.rpc.set_system_led(
                leds=[{"color": "red", "period": 60, "duration": 20, "start": 0}]
            )
            self.light = True
            return True
        except APIError:
            return False

    async def reboot(self) -> bool:
        try:
            await self.rpc.set_system_reboot()
            return True
        except APIError:
            return False

    async def restart_backend(self) -> bool:
        try:
            await self.rpc.set_miner_service("restart")
            return True
        except APIError:
            return False

    async def stop_mining(self) -> bool:
        try:
            await self.rpc.set_miner_service("stop")
            return True
        except APIError:
            return False

    async def resume_mining(self) -> bool:
        try:
            await self.rpc.set_miner_service("start")
            return True
        except APIError:
            return False

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            await self.rpc.set_miner_power_limit(wattage)
        except Exception as e:
            logging.warning(f"{self} set_power_limit: {e}")
            return False
        else:
            return True

    async def _get_mac(
        self,
        rpc_get_device_info: BTMinerV3DeviceInfoMsg | None = None,
    ) -> str | None:
        if rpc_get_device_info is None:
            try:
                rpc_get_device_info = await self.rpc.get_device_info()
            except APIError:
                return None
        if rpc_get_device_info.network.mac:
            return rpc_get_device_info.network.mac
        return None

    async def _get_api_version(
        self,
        rpc_get_device_info: BTMinerV3DeviceInfoMsg | None = None,
    ) -> str | None:
        if rpc_get_device_info is None:
            try:
                rpc_get_device_info = await self.rpc.get_device_info()
            except APIError:
                return None
        if rpc_get_device_info.system.api:
            return rpc_get_device_info.system.api
        return None

    async def _get_firmware_version(
        self,
        rpc_get_device_info: BTMinerV3DeviceInfoMsg | None = None,
    ) -> str | None:
        if rpc_get_device_info is None:
            try:
                rpc_get_device_info = await self.rpc.get_device_info()
            except APIError:
                return None
        if rpc_get_device_info.system.fwversion:
            return rpc_get_device_info.system.fwversion
        return None

    async def _get_hostname(
        self,
        rpc_get_device_info: BTMinerV3DeviceInfoMsg | None = None,
    ) -> str | None:
        if rpc_get_device_info is None:
            try:
                rpc_get_device_info = await self.rpc.get_device_info()
            except APIError:
                return None
        if rpc_get_device_info.network.hostname:
            return rpc_get_device_info.network.hostname
        return None

    async def _get_light_flashing(
        self,
        rpc_get_device_info: BTMinerV3DeviceInfoMsg | None = None,
    ) -> bool | None:
        if rpc_get_device_info is None:
            try:
                rpc_get_device_info = await self.rpc.get_device_info()
            except APIError:
                return None
        if rpc_get_device_info.system.ledstatus is not None:
            return rpc_get_device_info.system.ledstatus != "auto"
        return None

    async def _get_wattage_limit(
        self,
        rpc_get_device_info: BTMinerV3DeviceInfoMsg | None = None,
    ) -> int | None:
        if rpc_get_device_info is None:
            try:
                rpc_get_device_info = await self.rpc.get_device_info()
            except APIError:
                return None
        try:
            if rpc_get_device_info.miner.power_limit_set is not None:
                return int(float(rpc_get_device_info.miner.power_limit_set))
        except (ValueError, TypeError):
            pass
        return None

    async def _get_fans(
        self,
        rpc_get_miner_status_summary: BTMinerV3Summary | None = None,
    ) -> list[Fan]:
        if rpc_get_miner_status_summary is None:
            try:
                rpc_get_miner_status_summary = await self.rpc.get_miner_status_summary()
            except APIError:
                return []
        fans = []
        if rpc_get_miner_status_summary.fan_speed_in is not None:
            fans.append(Fan(speed=rpc_get_miner_status_summary.fan_speed_in))
        if rpc_get_miner_status_summary.fan_speed_out is not None:
            fans.append(Fan(speed=rpc_get_miner_status_summary.fan_speed_out))
        return fans

    async def _get_psu_fans(
        self,
        rpc_get_device_info: BTMinerV3DeviceInfoMsg | None = None,
    ) -> list[Fan]:
        if rpc_get_device_info is None:
            try:
                rpc_get_device_info = await self.rpc.get_device_info()
            except APIError:
                return []
        rpm = rpc_get_device_info.power.fanspeed
        return [Fan(speed=rpm)] if rpm is not None else []

    async def _get_hashboards(
        self,
        rpc_get_device_info: BTMinerV3DeviceInfoMsg | None = None,
        rpc_get_miner_status_edevs: list[BTMinerV3EdevItem] | None = None,
    ) -> list[HashBoard]:
        if rpc_get_device_info is None:
            try:
                rpc_get_device_info = await self.rpc.get_device_info()
            except APIError:
                return []
        if rpc_get_miner_status_edevs is None:
            try:
                rpc_get_miner_status_edevs = await self.rpc.get_miner_status_edevs()
            except APIError:
                return []

        boards = []
        board_count = rpc_get_device_info.hardware.boards
        edevs = rpc_get_miner_status_edevs
        for idx in range(board_count):
            board_data = edevs[idx] if idx < len(edevs) else None
            if board_data is None:
                boards.append(
                    HashBoard(
                        slot=idx,
                        expected_chips=self.expected_chips,
                        missing=True,
                    )
                )
                continue
            boards.append(
                HashBoard(
                    slot=idx,
                    hashrate=self.algo.hashrate(
                        rate=board_data.hash_average or 0,
                        unit=self.algo.unit.TH,  # type: ignore[attr-defined]
                    ).into(
                        self.algo.unit.default  # type: ignore[attr-defined]
                    ),
                    temp=board_data.chip_temp_min,
                    inlet_temp=board_data.chip_temp_min,
                    outlet_temp=board_data.chip_temp_max,
                    serial_number=getattr(
                        rpc_get_device_info.miner, f"pcbsn{idx}", None
                    ),
                    chips=board_data.effective_chips,
                    expected_chips=self.expected_chips,
                    active=(board_data.hash_average or 0) > 0,
                    missing=False,
                    tuned=True,
                )
            )
        return boards

    async def _get_pools(
        self,
        rpc_get_miner_status_pools: list[BTMinerV3Pool] | None = None,
    ) -> list[PoolMetrics]:
        if rpc_get_miner_status_pools is None:
            try:
                rpc_get_miner_status_pools = await self.rpc.get_miner_status_pools()
            except APIError:
                return []
        pools = []
        for idx, pool in enumerate(rpc_get_miner_status_pools):
            pools.append(
                PoolMetrics(
                    index=idx,
                    user=pool.account,
                    alive=pool.status == "alive",
                    active=pool.stratum_active,
                    url=PoolUrl.from_str(pool.url) if pool.url else None,
                )
            )
        return pools

    async def _get_uptime(
        self,
        rpc_get_miner_status_summary: BTMinerV3Summary | None = None,
    ) -> int | None:
        if rpc_get_miner_status_summary is None:
            try:
                rpc_get_miner_status_summary = await self.rpc.get_miner_status_summary()
            except APIError:
                return None
        if rpc_get_miner_status_summary.elapsed is not None:
            return rpc_get_miner_status_summary.elapsed
        return None

    async def _get_hashrate(
        self,
        rpc_get_miner_status_summary: BTMinerV3Summary | None = None,
    ) -> AlgoHashRateType | None:
        if rpc_get_miner_status_summary is None:
            try:
                rpc_get_miner_status_summary = await self.rpc.get_miner_status_summary()
            except APIError:
                return None
        try:
            return self.algo.hashrate(
                rate=rpc_get_miner_status_summary.hash_1min,
                unit=self.algo.unit.TH,  # type: ignore[attr-defined]
            ).into(self.algo.unit.default)  # type: ignore[attr-defined]
        except (ValueError, TypeError):
            pass
        return None

    async def _get_expected_hashrate(
        self,
        rpc_get_miner_status_summary: BTMinerV3Summary | None = None,
    ) -> AlgoHashRateType | None:
        if rpc_get_miner_status_summary is None:
            try:
                rpc_get_miner_status_summary = await self.rpc.get_miner_status_summary()
            except APIError:
                return None
        try:
            return self.algo.hashrate(
                rate=rpc_get_miner_status_summary.factory_hash,
                unit=self.algo.unit.TH,  # type: ignore[attr-defined]
            ).into(self.algo.unit.default)  # type: ignore[attr-defined]
        except (ValueError, TypeError):
            pass
        return None

    async def _get_wattage(
        self,
        rpc_get_miner_status_summary: BTMinerV3Summary | None = None,
    ) -> int | None:
        if rpc_get_miner_status_summary is None:
            try:
                rpc_get_miner_status_summary = await self.rpc.get_miner_status_summary()
            except APIError:
                return None
        try:
            return int(rpc_get_miner_status_summary.power_rate)
        except (ValueError, TypeError):
            pass
        return None

    async def _get_env_temp(
        self,
        rpc_get_miner_status_summary: BTMinerV3Summary | None = None,
    ) -> float | None:
        if rpc_get_miner_status_summary is None:
            try:
                rpc_get_miner_status_summary = await self.rpc.get_miner_status_summary()
            except APIError:
                return None
        return rpc_get_miner_status_summary.environment_temperature
