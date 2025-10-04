from typing import Any

from pydantic import BaseModel, ValidationError

from pyasic.config import MinerConfig
from pyasic.data.boards import HashBoard
from pyasic.data.fans import Fan
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm import MinerAlgo
from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
from pyasic.miners.device.firmware import StockFirmware
from pyasic.web.iceriver import IceRiverWebAPI


class IceRiverBoardInfo(BaseModel):
    no: int
    outtmp: float
    intmp: float
    rtpow: str
    chipnum: int

    class Config:
        extra = "allow"


class IceRiverPoolInfo(BaseModel):
    no: int | None = None
    addr: str = ""
    user: str | None = None
    accepted: int = 0
    rejected: int = 0
    connect: bool = False
    state: int = 0

    class Config:
        extra = "allow"


class IceRiverData(BaseModel):
    mac: str
    host: str
    fans: list[int]
    unit: str
    rtpow: str
    locate: bool
    powstate: bool
    boards: list[IceRiverBoardInfo]
    runtime: str
    pools: list[IceRiverPoolInfo]

    class Config:
        extra = "allow"


class IceRiverUserPanel(BaseModel):
    data: IceRiverData

    class Config:
        extra = "allow"


class IceRiverUserPanelWrapper(BaseModel):
    userpanel: IceRiverUserPanel

    class Config:
        extra = "allow"


ICERIVER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_userpanel", "userpanel")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("web_userpanel", "userpanel")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_userpanel", "userpanel")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [WebAPICommand("web_userpanel", "userpanel")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [WebAPICommand("web_userpanel", "userpanel")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [WebAPICommand("web_userpanel", "userpanel")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [WebAPICommand("web_userpanel", "userpanel")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [WebAPICommand("web_userpanel", "userpanel")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [WebAPICommand("web_userpanel", "userpanel")],
        ),
    }
)


class IceRiver(StockFirmware):
    """Handler for IceRiver miners"""

    _web_cls = IceRiverWebAPI
    web: IceRiverWebAPI

    data_locations = ICERIVER_DATA_LOC

    async def fault_light_off(self) -> bool:
        try:
            await self.web.locate(False)
        except APIError:
            return False
        return True

    async def fault_light_on(self) -> bool:
        try:
            await self.web.locate(True)
        except APIError:
            return False
        return True

    async def get_config(self) -> MinerConfig:
        web_userpanel = await self.web.userpanel()

        return MinerConfig.from_iceriver(web_userpanel)

    async def _get_fans(self, web_userpanel: dict[str, Any] | None = None) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                return []

        if web_userpanel is not None:
            try:
                panel_response = IceRiverUserPanelWrapper.model_validate(web_userpanel)
                return [Fan(speed=spd) for spd in panel_response.userpanel.data.fans]
            except ValidationError:
                pass
        return []

    async def _get_mac(self, web_userpanel: dict[str, Any] | None = None) -> str | None:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                return None

        if web_userpanel is not None:
            try:
                panel_response = IceRiverUserPanelWrapper.model_validate(web_userpanel)
                return panel_response.userpanel.data.mac.upper().replace("-", ":")
            except ValidationError:
                pass
        return None

    async def _get_hostname(
        self, web_userpanel: dict[str, Any] | None = None
    ) -> str | None:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                return None

        if web_userpanel is not None:
            try:
                panel_response = IceRiverUserPanelWrapper.model_validate(web_userpanel)
                return panel_response.userpanel.data.host
            except ValidationError:
                pass
        return None

    async def _get_hashrate(
        self, web_userpanel: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                return None

        if web_userpanel is not None:
            try:
                panel_response = IceRiverUserPanelWrapper.model_validate(web_userpanel)
                base_unit = panel_response.userpanel.data.unit
                return self.algo.hashrate(
                    rate=float(
                        panel_response.userpanel.data.rtpow.replace(base_unit, "")
                    ),
                    unit=MinerAlgo.SHA256.unit.from_str(base_unit + "H"),
                ).into(MinerAlgo.SHA256.unit.default)
            except (ValidationError, ValueError):
                pass
        return None

    async def _get_fault_light(
        self, web_userpanel: dict[str, Any] | None = None
    ) -> bool:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        if web_userpanel is not None:
            try:
                panel_response = IceRiverUserPanelWrapper.model_validate(web_userpanel)
                return panel_response.userpanel.data.locate
            except ValidationError:
                pass
        return False

    async def _is_mining(
        self, web_userpanel: dict[str, Any] | None = None
    ) -> bool | None:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                return False

        if web_userpanel is not None:
            try:
                panel_response = IceRiverUserPanelWrapper.model_validate(web_userpanel)
                return panel_response.userpanel.data.powstate
            except ValidationError:
                pass
        return False

    async def _get_hashboards(
        self, web_userpanel: dict[str, Any] | None = None
    ) -> list[HashBoard]:
        if self.expected_hashboards is None:
            return []

        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        hb_list = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if web_userpanel is not None:
            try:
                panel_response = IceRiverUserPanelWrapper.model_validate(web_userpanel)
                for board in panel_response.userpanel.data.boards:
                    idx = board.no - 1
                    hb_list[idx].chip_temp = round(board.outtmp)
                    hb_list[idx].temp = round(board.intmp)
                    hb_list[idx].hashrate = self.algo.hashrate(
                        rate=float(board.rtpow.replace("G", "")),
                        unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                    ).into(
                        self.algo.unit.default  # type: ignore[attr-defined]
                    )
                    hb_list[idx].chips = board.chipnum
                    hb_list[idx].missing = False
            except (ValidationError, ValueError):
                pass
        return hb_list

    async def _get_uptime(
        self, web_userpanel: dict[str, Any] | None = None
    ) -> int | None:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        if web_userpanel is not None:
            try:
                panel_response = IceRiverUserPanelWrapper.model_validate(web_userpanel)
                runtime = panel_response.userpanel.data.runtime
                days, hours, minutes, seconds = runtime.split(":")
                return (
                    (int(days) * 24 * 60 * 60)
                    + (int(hours) * 60 * 60)
                    + (int(minutes) * 60)
                    + int(seconds)
                )
            except (ValidationError, ValueError):
                pass
        return None

    async def _get_pools(
        self, web_userpanel: dict[str, Any] | None = None
    ) -> list[PoolMetrics]:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        pools_data = []
        if web_userpanel is not None:
            try:
                panel_response = IceRiverUserPanelWrapper.model_validate(web_userpanel)
                for pool_info in panel_response.userpanel.data.pools:
                    if pool_info.addr == "":
                        continue
                    pool_url = (
                        PoolUrl.from_str(pool_info.addr) if pool_info.addr else None
                    )
                    pool_data = PoolMetrics(
                        accepted=pool_info.accepted,
                        rejected=pool_info.rejected,
                        active=pool_info.connect,
                        alive=pool_info.state == 1,
                        url=pool_url,
                        user=pool_info.user,
                        index=pool_info.no,
                    )
                    pools_data.append(pool_data)
            except ValidationError:
                pass
        return pools_data
