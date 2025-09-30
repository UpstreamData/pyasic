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
from typing import Any

from pydantic import BaseModel, ValidationError

from pyasic.config import MinerConfig
from pyasic.config.mining import MiningModePreset
from pyasic.data.error_codes import VnishError
from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.errors import APIError
from pyasic.miners.backends.bmminer import BMMiner
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.miners.device.firmware import VNishFirmware
from pyasic.web.vnish import VNishWebAPI

VNISH_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [WebAPICommand("web_settings", "settings")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [WebAPICommand("web_summary", "summary")],
        ),
    }
)


class VnishSuccessResponse(BaseModel):
    success: bool


class VnishNetworkStatus(BaseModel):
    mac: str
    hostname: str

    class Config:
        extra = "allow"


class VnishSystemInfo(BaseModel):
    network_status: VnishNetworkStatus

    class Config:
        extra = "allow"


class VnishMinerStatus(BaseModel):
    miner_state: str

    class Config:
        extra = "allow"


class VnishOverclock(BaseModel):
    preset: str

    class Config:
        extra = "allow"


class VnishMinerInfo(BaseModel):
    power_usage: float
    miner_type: str
    miner_status: VnishMinerStatus
    overclock: VnishOverclock

    class Config:
        extra = "allow"


class VnishChainStatus(BaseModel):
    state: str
    description: str = ""

    class Config:
        extra = "allow"


class VnishChain(BaseModel):
    status: VnishChainStatus

    class Config:
        extra = "allow"


class VnishWebSummary(BaseModel):
    system: VnishSystemInfo
    miner: VnishMinerInfo
    chains: list[VnishChain] = []

    class Config:
        extra = "allow"


class VnishWebInfo(BaseModel):
    system: VnishSystemInfo

    class Config:
        extra = "allow"


class VnishWebSettings(BaseModel):
    miner: VnishMinerInfo

    class Config:
        extra = "allow"


class VnishFindMinerResponse(BaseModel):
    on: bool

    class Config:
        extra = "allow"


class VNish(VNishFirmware, BMMiner):
    """Handler for VNish miners"""

    _web_cls = VNishWebAPI
    web: VNishWebAPI

    supports_shutdown = True
    supports_presets = True
    supports_autotuning = True

    data_locations = VNISH_DATA_LOC

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        await self.web.post_settings(
            miner_settings=config.as_vnish(user_suffix=user_suffix)
        )

    async def restart_backend(self) -> bool:
        data = await self.web.restart_vnish()
        if data:
            try:
                response = VnishSuccessResponse.model_validate(data)
                return response.success
            except ValidationError:
                pass
        return False

    async def stop_mining(self) -> bool:
        data = await self.web.stop_mining()
        if data:
            try:
                response = VnishSuccessResponse.model_validate(data)
                return response.success
            except ValidationError:
                pass
        return False

    async def resume_mining(self) -> bool:
        data = await self.web.resume_mining()
        if data:
            try:
                response = VnishSuccessResponse.model_validate(data)
                return response.success
            except ValidationError:
                pass
        return False

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            try:
                response = VnishSuccessResponse.model_validate(data)
                return response.success
            except ValidationError:
                pass
        return False

    async def _get_mac(self, web_summary: dict[str, Any] | None = None) -> str | None:
        if web_summary is not None:
            try:
                summary = VnishWebSummary.model_validate(web_summary)
                return summary.system.network_status.mac
            except ValidationError:
                pass

        web_info = await self.web.info()

        if web_info is not None:
            try:
                info = VnishWebInfo.model_validate(web_info)
                return info.system.network_status.mac
            except ValidationError:
                pass

        return None

    async def fault_light_off(self) -> bool:
        result = await self.web.find_miner()
        if result is not None:
            try:
                response = VnishFindMinerResponse.model_validate(result)
                if not response.on:
                    return True
                else:
                    await self.web.find_miner()
            except ValidationError:
                pass
        return False

    async def fault_light_on(self) -> bool:
        result = await self.web.find_miner()
        if result is not None:
            try:
                response = VnishFindMinerResponse.model_validate(result)
                if response.on:
                    return True
                else:
                    await self.web.find_miner()
            except ValidationError:
                pass
        return False

    async def _get_hostname(
        self, web_summary: dict[str, Any] | None = None
    ) -> str | None:
        if web_summary is None:
            web_info = await self.web.info()
            if web_info is not None:
                try:
                    info = VnishWebInfo.model_validate(web_info)
                    return info.system.network_status.hostname
                except ValidationError:
                    pass
        else:
            try:
                summary = VnishWebSummary.model_validate(web_summary)
                return summary.system.network_status.hostname
            except ValidationError:
                pass

        return None

    async def _get_wattage(
        self, web_summary: dict[str, Any] | None = None
    ) -> int | None:
        if web_summary is None:
            web_summary = await self.web.summary()

        if web_summary is not None:
            try:
                summary = VnishWebSummary.model_validate(web_summary)
                return round(summary.miner.power_usage)
            except ValidationError:
                pass
        return None

    async def _get_hashrate(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        # get hr from API
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                return None

        if rpc_summary is not None:
            try:
                return self.algo.hashrate(
                    rate=float(rpc_summary["SUMMARY"][0]["GHS 5s"]),
                    unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except (LookupError, ValueError, TypeError):
                pass

        return None

    async def _get_wattage_limit(
        self, web_settings: dict[str, Any] | None = None
    ) -> int | None:
        if web_settings is None:
            web_settings = await self.web.summary()

        if web_settings is not None:
            try:
                summary = VnishWebSummary.model_validate(web_settings)
                preset = summary.miner.overclock.preset
                if preset == "disabled":
                    return None
                if preset.isdigit():
                    return int(preset)
            except ValidationError:
                pass

        return None

    async def _get_fw_ver(
        self, web_summary: dict[str, Any] | None = None
    ) -> str | None:
        if web_summary is None:
            web_summary = await self.web.summary()

        if web_summary is not None:
            try:
                summary = VnishWebSummary.model_validate(web_summary)
                fw_ver = summary.miner.miner_type
                if "(Vnish " in fw_ver:
                    fw_ver = fw_ver.split("(Vnish ")[1].replace(")", "")
                    return fw_ver
            except (ValidationError, IndexError):
                pass
        return None

    async def _is_mining(
        self, web_summary: dict[str, Any] | None = None
    ) -> bool | None:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                return None

        if web_summary is not None:
            try:
                summary = VnishWebSummary.model_validate(web_summary)
                state = summary.miner.miner_status.miner_state
                return state not in ["stopped", "shutting-down", "failure"]
            except ValidationError:
                pass

        return None

    async def _get_errors(  # type: ignore[override]
        self, web_summary: dict[str, Any] | None = None
    ) -> list[VnishError]:
        errors: list[VnishError] = []

        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                return errors

        if web_summary is not None:
            try:
                summary = VnishWebSummary.model_validate(web_summary)
                for chain in summary.chains:
                    if chain.status.state == "failure":
                        errors.append(
                            VnishError(error_message=chain.status.description)
                        )
            except ValidationError:
                pass

        return errors

    async def get_config(self) -> MinerConfig:
        try:
            web_settings = await self.web.settings()
            web_presets_dict = await self.web.autotune_presets()
            web_presets = (
                web_presets_dict.get("presets", []) if web_presets_dict else []
            )
            web_perf_summary = (await self.web.perf_summary()) or {}
        except APIError:
            return self.config or MinerConfig()
        self.config = MinerConfig.from_vnish(
            web_settings, web_presets, web_perf_summary
        )
        return self.config

    async def set_power_limit(self, wattage: int) -> bool:
        config = await self.get_config()

        # Check if mining mode is preset mode and has available presets
        if not isinstance(config.mining_mode, MiningModePreset):
            return False

        valid_presets = [
            preset.power
            for preset in config.mining_mode.available_presets
            if (preset.tuned and preset.power is not None and preset.power <= wattage)
        ]

        if not valid_presets:
            return False

        new_wattage = max(valid_presets)

        # Set power to highest preset <= wattage
        try:
            await self.web.set_power_limit(new_wattage)
            updated_settings = await self.web.settings()
        except APIError:
            raise
        except Exception as e:
            logging.warning(f"{self} - Failed to set power limit: {e}")
            return False

        if int(updated_settings["miner"]["overclock"]["preset"]) == new_wattage:
            return True
        else:
            return False
