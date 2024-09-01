from typing import List, Optional

from pyasic.data import AlgoHashRate, Fan, HashBoard, HashUnit
from pyasic.device import MinerAlgo
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
from pyasic.miners.device.firmware import StockFirmware
from pyasic.web.iceriver import IceRiverWebAPI

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

    async def _get_fans(self, web_userpanel: dict = None) -> List[Fan]:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        if web_userpanel is not None:
            try:
                return [Fan(spd) for spd in web_userpanel["fans"]]
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_mac(self, web_userpanel: dict = None) -> Optional[str]:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        if web_userpanel is not None:
            try:
                return web_userpanel["mac"].upper().replace("-", ":")
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_hostname(self, web_userpanel: dict = None) -> Optional[str]:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        if web_userpanel is not None:
            try:
                return web_userpanel["host"]
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_hashrate(self, web_userpanel: dict = None) -> Optional[AlgoHashRate]:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        if web_userpanel is not None:
            try:
                base_unit = web_userpanel["unit"]
                return AlgoHashRate.SHA256(
                    float(web_userpanel["rtpow"].replace(base_unit, "")),
                    unit=MinerAlgo.SHA256.unit.from_str(base_unit + "H"),
                ).into(MinerAlgo.SHA256.unit.default)
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_fault_light(self, web_userpanel: dict = None) -> bool:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        if web_userpanel is not None:
            try:
                return web_userpanel["locate"]
            except (LookupError, ValueError, TypeError):
                pass
        return False

    async def _is_mining(self, web_userpanel: dict = None) -> Optional[bool]:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        if web_userpanel is not None:
            try:
                return web_userpanel["powstate"]
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_hashboards(self, web_userpanel: dict = None) -> List[HashBoard]:
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
                for board in web_userpanel["boards"]:
                    idx = board["no"] - 1
                    hb_list[idx].chip_temp = round(board["outtmp"])
                    hb_list[idx].temp = round(board["intmp"])
                    hb_list[idx].hashrate = AlgoHashRate.SHA256(
                        float(board["rtpow"].replace("G", "")), HashUnit.SHA256.GH
                    ).into(self.algo.unit.default)
                    hb_list[idx].chips = board["chipnum"]
                    hb_list[idx].missing = False
            except LookupError:
                pass
        return hb_list

    async def _get_uptime(self, web_userpanel: dict = None) -> Optional[int]:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        if web_userpanel is not None:
            try:
                runtime = web_userpanel["runtime"]
                days, hours, minutes, seconds = runtime.split(":")
                return (
                    (int(days) * 24 * 60 * 60)
                    + (int(hours) * 60 * 60)
                    + (int(minutes) * 60)
                    + int(seconds)
                )
            except (LookupError, ValueError, TypeError):
                pass
