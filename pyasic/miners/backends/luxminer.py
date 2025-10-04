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

from pydantic import BaseModel, Field, ValidationError

from pyasic.config import MinerConfig
from pyasic.config.mining import MiningModePreset
from pyasic.data.boards import HashBoard
from pyasic.data.fans import Fan
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, RPCAPICommand
from pyasic.miners.device.firmware import LuxOSFirmware
from pyasic.rpc.luxminer import LUXMinerRPCAPI


class LuxConfigResponse(BaseModel):
    MACAddr: str
    RedLed: str = "off"

    class Config:
        extra = "allow"


class LuxConfigWrapper(BaseModel):
    CONFIG: list[LuxConfigResponse]

    class Config:
        extra = "allow"


class LuxSummaryResponse(BaseModel):
    GHS_5s: float = Field(alias="GHS 5s")

    class Config:
        extra = "allow"
        populate_by_name = True


class LuxSummaryWrapper(BaseModel):
    SUMMARY: list[LuxSummaryResponse]

    class Config:
        extra = "allow"


class LuxPowerResponse(BaseModel):
    Watts: float | int

    class Config:
        extra = "allow"


class LuxPowerWrapper(BaseModel):
    POWER: list[LuxPowerResponse]

    class Config:
        extra = "allow"


class LuxStatsResponse(BaseModel):
    Elapsed: int
    total_rateideal: float
    rate_unit: str = "GH"
    chain_rate1: float = 0
    chain_rate2: float = 0
    chain_rate3: float = 0
    chain_acn1: int = 0
    chain_acn2: int = 0
    chain_acn3: int = 0
    temp_chip1: str = "0-0-0-0"
    temp_chip2: str = "0-0-0-0"
    temp_chip3: str = "0-0-0-0"
    temp_pcb1: str = "0-0-0-0"
    temp_pcb2: str = "0-0-0-0"
    temp_pcb3: str = "0-0-0-0"

    class Config:
        extra = "allow"


class LuxStatsWrapper(BaseModel):
    STATS: list[Any]

    class Config:
        extra = "allow"


class LuxFanResponse(BaseModel):
    RPM: int

    class Config:
        extra = "allow"


class LuxFansWrapper(BaseModel):
    FANS: list[LuxFanResponse]

    class Config:
        extra = "allow"


class LuxVersionResponse(BaseModel):
    Miner: str
    API: str

    class Config:
        extra = "allow"


class LuxVersionWrapper(BaseModel):
    VERSION: list[LuxVersionResponse]

    class Config:
        extra = "allow"


class LuxPoolInfo(BaseModel):
    URL: str | None = None
    User: str | None = None
    Status: str = ""
    Stratum_Active: bool = Field(False, alias="Stratum Active")
    Accepted: int = 0
    Rejected: int = 0
    Get_Failures: int = Field(0, alias="Get Failures")
    Remote_Failures: int = Field(0, alias="Remote Failures")
    POOL: int = 0

    class Config:
        extra = "allow"
        populate_by_name = True


class LuxPoolsWrapper(BaseModel):
    POOLS: list[LuxPoolInfo]

    class Config:
        extra = "allow"


class LuxATMResponse(BaseModel):
    Enabled: bool

    class Config:
        extra = "allow"


class LuxATMWrapper(BaseModel):
    ATM: list[LuxATMResponse]

    class Config:
        extra = "allow"


class LuxProfileResponse(BaseModel):
    Profile: str

    class Config:
        extra = "allow"


class LuxProfileWrapper(BaseModel):
    PROFILE: list[LuxProfileResponse]

    class Config:
        extra = "allow"


LUXMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [RPCAPICommand("rpc_config", "config")],
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
            [RPCAPICommand("rpc_power", "power")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [
                RPCAPICommand("rpc_config", "config"),
                RPCAPICommand("rpc_profiles", "profiles"),
            ],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_fans", "fans")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime", [RPCAPICommand("rpc_stats", "stats")]
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools", [RPCAPICommand("rpc_pools", "pools")]
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver", [RPCAPICommand("rpc_version", "version")]
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver", [RPCAPICommand("rpc_version", "version")]
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light", [RPCAPICommand("rpc_config", "config")]
        ),
    }
)


class LUXMiner(LuxOSFirmware):
    """Handler for LuxOS miners"""

    _rpc_cls = LUXMinerRPCAPI
    rpc: LUXMinerRPCAPI

    supports_shutdown = True
    supports_presets = True
    supports_autotuning = True

    data_locations = LUXMINER_DATA_LOC

    async def fault_light_on(self) -> bool:
        try:
            await self.rpc.ledset("red", "blink")
            return True
        except (APIError, LookupError):
            pass
        return False

    async def fault_light_off(self) -> bool:
        try:
            await self.rpc.ledset("red", "off")
            return True
        except (APIError, LookupError):
            pass
        return False

    async def restart_backend(self) -> bool:
        return await self.restart_luxminer()

    async def restart_luxminer(self) -> bool:
        try:
            await self.rpc.resetminer()
            return True
        except (APIError, LookupError):
            pass
        return False

    async def stop_mining(self) -> bool:
        try:
            await self.rpc.sleep()
            return True
        except (APIError, LookupError):
            pass
        return False

    async def resume_mining(self) -> bool:
        try:
            await self.rpc.wakeup()
            return True
        except (APIError, LookupError):
            pass
        return False

    async def reboot(self) -> bool:
        try:
            await self.rpc.rebootdevice()
            return True
        except (APIError, LookupError):
            pass
        return False

    async def get_config(self) -> MinerConfig:
        data = await self.rpc.multicommand(
            "tempctrl", "fans", "pools", "groups", "config", "profiles"
        )
        return MinerConfig.from_luxos(
            rpc_tempctrl=data.get("tempctrl", [{}])[0],
            rpc_fans=data.get("fans", [{}])[0],
            rpc_pools=data.get("pools", [{}])[0],
            rpc_groups=data.get("groups", [{}])[0],
            rpc_config=data.get("config", [{}])[0],
            rpc_profiles=data.get("profiles", [{}])[0],
        )

    async def upgrade_firmware(self, *args: Any, **kwargs: Any) -> bool:
        """
        Upgrade the firmware on a LuxOS miner by calling the 'updaterun' API command.
        Returns:
            bool: True if the firmware upgrade was successfully initiated, False otherwise.
        """
        try:
            await self.rpc.updaterun()
            logging.info(f"{self.ip}: Firmware upgrade initiated successfully.")
            return True

        except APIError as e:
            logging.error(f"{self.ip}: Firmware upgrade failed: {e}")

        return False

    async def atm_enabled(self) -> bool | None:
        try:
            result = await self.rpc.atm()
            atm_response = LuxATMWrapper.model_validate(result)
            return atm_response.ATM[0].Enabled
        except (APIError, ValidationError):
            pass
        return None

    async def set_power_limit(self, wattage: int) -> bool:
        config = await self.get_config()

        # Check if we have preset mode with available presets
        if not hasattr(config.mining_mode, "available_presets"):
            logging.warning(f"{self} - Mining mode does not support presets")
            return False

        available_presets = getattr(config.mining_mode, "available_presets", [])
        if not available_presets:
            logging.warning(f"{self} - No available presets found")
            return False

        valid_presets = {
            preset.name: preset.power
            for preset in available_presets
            if preset.power is not None and preset.power <= wattage
        }

        if not valid_presets:
            logging.warning(f"{self} - No valid presets found for wattage {wattage}")
            return False

        # Set power to highest preset <= wattage
        # If ATM enabled, must disable it before setting power limit
        new_preset = max(valid_presets, key=lambda x: valid_presets[x])

        re_enable_atm = False
        try:
            if await self.atm_enabled():
                re_enable_atm = True
                await self.rpc.atmset(enabled=False)
            result = await self.rpc.profileset(new_preset)
            if re_enable_atm:
                await self.rpc.atmset(enabled=True)
        except APIError:
            raise
        except Exception as e:
            logging.warning(f"{self} - Failed to set power limit: {e}")
            return False

        try:
            profile_response = LuxProfileWrapper.model_validate(result)
            return bool(profile_response.PROFILE[0].Profile == new_preset)
        except ValidationError:
            return False

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(self, rpc_config: dict[str, Any] | None = None) -> str | None:
        if rpc_config is None:
            try:
                rpc_config = await self.rpc.config()
            except APIError:
                pass

        if rpc_config is not None:
            try:
                config_response = LuxConfigWrapper.model_validate(rpc_config)
                return config_response.CONFIG[0].MACAddr.upper()
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
                summary_response = LuxSummaryWrapper.model_validate(rpc_summary)
                return self.algo.hashrate(
                    rate=summary_response.SUMMARY[0].GHS_5s,
                    unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except ValidationError:
                pass
        return None

    async def _get_hashboards(
        self, rpc_stats: dict[str, Any] | None = None
    ) -> list[HashBoard]:
        if self.expected_hashboards is None:
            return []

        hashboards = [
            HashBoard(slot=idx, expected_chips=self.expected_chips)
            for idx in range(self.expected_hashboards)
        ]

        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass
        if rpc_stats is not None:
            try:
                # TODO: bugged on S9 because of index issues, fix later.
                stats_wrapper = LuxStatsWrapper.model_validate(rpc_stats)
                if len(stats_wrapper.STATS) > 1:
                    board_stats = LuxStatsResponse.model_validate(
                        stats_wrapper.STATS[1]
                    )
                    for idx in range(3):
                        board_n = idx + 1
                        chain_rate = getattr(board_stats, f"chain_rate{board_n}", 0)
                        hashboards[idx].hashrate = self.algo.hashrate(
                            rate=chain_rate,
                            unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                        ).into(
                            self.algo.unit.default  # type: ignore[attr-defined]
                        )
                        hashboards[idx].chips = getattr(
                            board_stats, f"chain_acn{board_n}", 0
                        )
                        chip_temp_str = getattr(
                            board_stats, f"temp_chip{board_n}", "0-0-0-0"
                        )
                        chip_temp_data = list(
                            filter(
                                lambda x: not x == 0,
                                map(int, chip_temp_str.split("-")),
                            )
                        )
                        if len(chip_temp_data) >= 4:
                            hashboards[idx].chip_temp = (
                                sum([chip_temp_data[0], chip_temp_data[3]]) / 2
                            )
                        board_temp_str = getattr(
                            board_stats, f"temp_pcb{board_n}", "0-0-0-0"
                        )
                        board_temp_data = list(
                            filter(
                                lambda x: not x == 0,
                                map(int, board_temp_str.split("-")),
                            )
                        )
                        if len(board_temp_data) >= 3:
                            hashboards[idx].temp = (
                                sum([board_temp_data[1], board_temp_data[2]]) / 2
                            )
                        hashboards[idx].missing = False
            except ValidationError:
                pass
        return hashboards

    async def _get_wattage(self, rpc_power: dict[str, Any] | None = None) -> int | None:
        if rpc_power is None:
            try:
                rpc_power = await self.rpc.power()
            except APIError:
                pass

        if rpc_power is not None:
            try:
                power_response = LuxPowerWrapper.model_validate(rpc_power)
                return round(power_response.POWER[0].Watts)
            except ValidationError:
                pass
        return None

    async def _get_wattage_limit(
        self,
        rpc_config: dict[str, Any] | None = None,
        rpc_profiles: dict[str, Any] | None = None,
    ) -> int | None:
        if rpc_config is None or rpc_profiles is None:
            return None
        try:
            active_preset = MiningModePreset.get_active_preset_from_luxos(
                rpc_config, rpc_profiles
            )
            return active_preset.power
        except (LookupError, ValueError, TypeError):
            pass
        return None

    async def _get_fans(self, rpc_fans: dict[str, Any] | None = None) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if rpc_fans is None:
            try:
                rpc_fans = await self.rpc.fans()
            except APIError:
                pass

        fans = []

        if rpc_fans is not None:
            try:
                fans_response = LuxFansWrapper.model_validate(rpc_fans)
                for fan_idx in range(self.expected_fans):
                    if fan_idx < len(fans_response.FANS):
                        fans.append(Fan(speed=fans_response.FANS[fan_idx].RPM))
                    else:
                        fans.append(Fan())
            except ValidationError:
                fans = [Fan() for _ in range(self.expected_fans)]
        else:
            fans = [Fan() for _ in range(self.expected_fans)]
        return fans

    async def _get_expected_hashrate(
        self, rpc_stats: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                stats_wrapper = LuxStatsWrapper.model_validate(rpc_stats)
                if len(stats_wrapper.STATS) > 1:
                    stats_response = LuxStatsResponse.model_validate(
                        stats_wrapper.STATS[1]
                    )
                    return self.algo.hashrate(
                        rate=stats_response.total_rateideal,
                        unit=self.algo.unit.from_str(stats_response.rate_unit),
                    ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except ValidationError:
                pass
        return None

    async def _get_uptime(self, rpc_stats: dict[str, Any] | None = None) -> int | None:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                stats_wrapper = LuxStatsWrapper.model_validate(rpc_stats)
                if len(stats_wrapper.STATS) > 1:
                    stats_response = LuxStatsResponse.model_validate(
                        stats_wrapper.STATS[1]
                    )
                    return stats_response.Elapsed
            except ValidationError:
                pass
        return None

    async def _get_fw_ver(
        self, rpc_version: dict[str, Any] | None = None
    ) -> str | None:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                pass

        if rpc_version is not None:
            try:
                version_response = LuxVersionWrapper.model_validate(rpc_version)
                return version_response.VERSION[0].Miner
            except ValidationError:
                pass
        return None

    async def _get_api_ver(
        self, rpc_version: dict[str, Any] | None = None
    ) -> str | None:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                pass

        if rpc_version is not None:
            try:
                version_response = LuxVersionWrapper.model_validate(rpc_version)
                return version_response.VERSION[0].API
            except ValidationError:
                pass
        return None

    async def _get_fault_light(
        self, rpc_config: dict[str, Any] | None = None
    ) -> bool | None:
        if rpc_config is None:
            try:
                rpc_config = await self.rpc.config()
            except APIError:
                pass

        if rpc_config is not None:
            try:
                config_response = LuxConfigWrapper.model_validate(rpc_config)
                return config_response.CONFIG[0].RedLed != "off"
            except ValidationError:
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
                pools_response = LuxPoolsWrapper.model_validate(rpc_pools)
                for pool_info in pools_response.POOLS:
                    pool_url = (
                        PoolUrl.from_str(pool_info.URL) if pool_info.URL else None
                    )
                    pool_data = PoolMetrics(
                        accepted=pool_info.Accepted,
                        rejected=pool_info.Rejected,
                        get_failures=pool_info.Get_Failures,
                        remote_failures=pool_info.Remote_Failures,
                        active=pool_info.Stratum_Active,
                        alive=pool_info.Status == "Alive",
                        url=pool_url,
                        user=pool_info.User,
                        index=pool_info.POOL,
                    )
                    pools_data.append(pool_data)
            except ValidationError:
                pass
        return pools_data
