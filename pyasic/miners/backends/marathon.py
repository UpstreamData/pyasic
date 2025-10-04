from typing import Any

from pydantic import BaseModel, Field, ValidationError

from pyasic.config import MinerConfig, MiningModeConfig
from pyasic.data.boards import HashBoard
from pyasic.data.fans import Fan
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
from pyasic.miners.device.firmware import MaraFirmware
from pyasic.misc import merge_dicts
from pyasic.rpc.marathon import MaraRPCAPI
from pyasic.web.marathon import MaraWebAPI


class MaraBriefResponse(BaseModel):
    power_consumption_estimated: float
    status: str
    elapsed: int
    hashrate_realtime: float
    hashrate_ideal: float

    class Config:
        extra = "allow"


class MaraOverviewResponse(BaseModel):
    mac: str
    version_firmware: str

    class Config:
        extra = "allow"


class MaraNetworkConfigResponse(BaseModel):
    hostname: str

    class Config:
        extra = "allow"


class MaraHashboardInfo(BaseModel):
    index: int
    hashrate_average: float
    temperature_pcb: list[float]
    temperature_chip: list[float]
    asic_num: int
    serial_number: str

    class Config:
        extra = "allow"


class MaraHashboardsResponse(BaseModel):
    hashboards: list[MaraHashboardInfo]

    class Config:
        extra = "allow"


class MaraLocateMinerResponse(BaseModel):
    blinking: bool

    class Config:
        extra = "allow"


class MaraConcordeMode(BaseModel):
    power_target: int = Field(alias="power-target")

    class Config:
        extra = "allow"
        populate_by_name = True


class MaraMinerMode(BaseModel):
    concorde: MaraConcordeMode

    class Config:
        extra = "allow"


class MaraMinerConfigResponse(BaseModel):
    mode: MaraMinerMode

    class Config:
        extra = "allow"


class MaraFanInfo(BaseModel):
    current_speed: int

    class Config:
        extra = "allow"


class MaraFansResponse(BaseModel):
    fans: list[MaraFanInfo]

    class Config:
        extra = "allow"


class MaraPoolInfo(BaseModel):
    url: str | None = None
    user: str | None = None
    status: str
    priority: int
    index: int
    accepted: int = 0
    rejected: int = 0
    stale: int = 0
    discarded: int = 0

    class Config:
        extra = "allow"


class MaraPoolsResponse(BaseModel):
    pools: list[MaraPoolInfo]

    class Config:
        extra = "allow"


MARA_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_overview", "overview")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_overview", "overview")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_network_config", "network_config")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [WebAPICommand("web_brief", "brief")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [WebAPICommand("web_brief", "brief")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [WebAPICommand("web_hashboards", "hashboards")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_brief", "brief")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [WebAPICommand("web_miner_config", "miner_config")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("web_fans", "fans")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [WebAPICommand("web_locate_miner", "locate_miner")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [WebAPICommand("web_brief", "brief")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [WebAPICommand("web_brief", "brief")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [WebAPICommand("web_pools", "pools")],
        ),
    }
)


class MaraMiner(MaraFirmware):
    _rpc_cls = MaraRPCAPI
    rpc: MaraRPCAPI
    _web_cls = MaraWebAPI
    web: MaraWebAPI

    data_locations = MARA_DATA_LOC

    async def fault_light_off(self) -> bool:
        res = await self.web.set_locate_miner(blinking=False)
        try:
            locate = MaraLocateMinerResponse.model_validate(res)
            return not locate.blinking
        except ValidationError:
            return False

    async def fault_light_on(self) -> bool:
        res = await self.web.set_locate_miner(blinking=True)
        try:
            locate = MaraLocateMinerResponse.model_validate(res)
            return locate.blinking
        except ValidationError:
            return False

    async def get_config(self) -> MinerConfig:
        data = await self.web.get_miner_config()
        if data:
            self.config = MinerConfig.from_mara(data)
            return self.config
        return MinerConfig()

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        data = await self.web.get_miner_config()
        cfg_data = config.as_mara(user_suffix=user_suffix)
        merged_cfg = merge_dicts(data, cfg_data)
        await self.web.set_miner_config(**merged_cfg)

    async def set_power_limit(self, wattage: int) -> bool:
        cfg = await self.get_config()
        cfg.mining_mode = MiningModeConfig.power_tuning(power=wattage)
        await self.send_config(cfg)
        return True

    async def stop_mining(self) -> bool:
        data = await self.web.get_miner_config()
        data["mode"]["work-mode-selector"] = "Sleep"
        await self.web.set_miner_config(**data)
        return True

    async def resume_mining(self) -> bool:
        data = await self.web.get_miner_config()
        data["mode"]["work-mode-selector"] = "Auto"
        await self.web.set_miner_config(**data)
        return True

    async def reboot(self) -> bool:
        await self.web.reboot()
        return True

    async def restart_backend(self) -> bool:
        await self.web.reload()
        return True

    async def _get_wattage(self, web_brief: dict[str, Any] | None = None) -> int | None:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                brief = MaraBriefResponse.model_validate(web_brief)
                return round(brief.power_consumption_estimated)
            except ValidationError:
                pass
        return None

    async def _is_mining(self, web_brief: dict[str, Any] | None = None) -> bool | None:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                brief = MaraBriefResponse.model_validate(web_brief)
                return brief.status == "Mining"
            except ValidationError:
                pass
        return None

    async def _get_uptime(self, web_brief: dict[str, Any] | None = None) -> int | None:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                brief = MaraBriefResponse.model_validate(web_brief)
                return brief.elapsed
            except ValidationError:
                pass
        return None

    async def _get_hashboards(
        self, web_hashboards: dict[str, Any] | None = None
    ) -> list[HashBoard]:
        if self.expected_hashboards is None:
            return []

        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if web_hashboards is None:
            try:
                web_hashboards = await self.web.hashboards()
            except APIError:
                pass

        if web_hashboards is not None:
            try:
                response = MaraHashboardsResponse.model_validate(web_hashboards)
                for hb in response.hashboards:
                    idx = hb.index
                    hashboards[idx].hashrate = self.algo.hashrate(
                        rate=hb.hashrate_average,
                        unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                    ).into(
                        self.algo.unit.default  # type: ignore[attr-defined]
                    )
                    if hb.temperature_pcb:
                        hashboards[idx].temp = round(
                            sum(hb.temperature_pcb) / len(hb.temperature_pcb)
                        )
                    if hb.temperature_chip:
                        hashboards[idx].chip_temp = round(
                            sum(hb.temperature_chip) / len(hb.temperature_chip)
                        )
                    hashboards[idx].chips = hb.asic_num
                    hashboards[idx].serial_number = hb.serial_number
                    hashboards[idx].missing = False
            except ValidationError:
                pass
        return hashboards

    async def _get_mac(self, web_overview: dict[str, Any] | None = None) -> str | None:
        if web_overview is None:
            try:
                web_overview = await self.web.overview()
            except APIError:
                pass

        if web_overview is not None:
            try:
                overview = MaraOverviewResponse.model_validate(web_overview)
                return overview.mac.upper()
            except ValidationError:
                pass
        return None

    async def _get_fw_ver(
        self, web_overview: dict[str, Any] | None = None
    ) -> str | None:
        if web_overview is None:
            try:
                web_overview = await self.web.overview()
            except APIError:
                pass

        if web_overview is not None:
            try:
                overview = MaraOverviewResponse.model_validate(web_overview)
                return overview.version_firmware
            except ValidationError:
                pass
        return None

    async def _get_hostname(
        self, web_network_config: dict[str, Any] | None = None
    ) -> str | None:
        if web_network_config is None:
            try:
                web_network_config = await self.web.get_network_config()
            except APIError:
                pass

        if web_network_config is not None:
            try:
                config = MaraNetworkConfigResponse.model_validate(web_network_config)
                return config.hostname
            except ValidationError:
                pass
        return None

    async def _get_hashrate(
        self, web_brief: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                brief = MaraBriefResponse.model_validate(web_brief)
                return self.algo.hashrate(
                    rate=brief.hashrate_realtime,
                    unit=self.algo.unit.TH,  # type: ignore[attr-defined]
                ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except ValidationError:
                pass
        return None

    async def _get_fans(self, web_fans: dict[str, Any] | None = None) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if web_fans is None:
            try:
                web_fans = await self.web.fans()
            except APIError:
                pass

        if web_fans is not None:
            try:
                response = MaraFansResponse.model_validate(web_fans)
                return [Fan(speed=fan.current_speed) for fan in response.fans]
            except ValidationError:
                pass

        return [Fan() for _ in range(self.expected_fans)]

    async def _get_fault_light(
        self, web_locate_miner: dict[str, Any] | None = None
    ) -> bool:
        if web_locate_miner is None:
            try:
                web_locate_miner = await self.web.get_locate_miner()
            except APIError:
                pass

        if web_locate_miner is not None:
            try:
                locate = MaraLocateMinerResponse.model_validate(web_locate_miner)
                return locate.blinking
            except ValidationError:
                pass
        return False

    async def _get_expected_hashrate(
        self, web_brief: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                brief = MaraBriefResponse.model_validate(web_brief)
                return self.algo.hashrate(
                    rate=brief.hashrate_ideal,
                    unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except ValidationError:
                pass
        return None

    async def _get_wattage_limit(
        self, web_miner_config: dict[str, Any] | None = None
    ) -> int | None:
        if web_miner_config is None:
            try:
                web_miner_config = await self.web.get_miner_config()
            except APIError:
                pass

        if web_miner_config is not None:
            try:
                config = MaraMinerConfigResponse.model_validate(web_miner_config)
                return config.mode.concorde.power_target
            except ValidationError:
                pass
        return None

    async def _get_pools(self, web_pools: list[Any] | None = None) -> list[PoolMetrics]:
        if web_pools is None:
            try:
                response = await self.web.pools()
                pools_response = MaraPoolsResponse.model_validate(response)
            except (APIError, ValidationError):
                return []
        else:
            try:
                pools_response = MaraPoolsResponse.model_validate({"pools": web_pools})
            except ValidationError:
                return []

        active_pool_index = None
        highest_priority = float("inf")

        for pool_info in pools_response.pools:
            if pool_info.status == "Alive" and pool_info.priority < highest_priority:
                highest_priority = pool_info.priority
                active_pool_index = pool_info.index

        pools_data = []
        for pool_info in pools_response.pools:
            pool_url = PoolUrl.from_str(pool_info.url) if pool_info.url else None
            pool_data = PoolMetrics(
                accepted=pool_info.accepted,
                rejected=pool_info.rejected,
                get_failures=pool_info.stale,
                remote_failures=pool_info.discarded,
                active=pool_info.index == active_pool_index,
                alive=pool_info.status == "Alive",
                url=pool_url,
                user=pool_info.user,
                index=pool_info.index,
            )
            pools_data.append(pool_data)

        return pools_data
