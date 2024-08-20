from typing import List, Optional

from pyasic.data import AlgoHashRate, Fan
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
                return web_userpanel["mac"].upper()
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
                return AlgoHashRate.SHA256(web_userpanel["rtpow"])
            except (LookupError, ValueError, TypeError):
                pass
