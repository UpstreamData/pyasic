from typing import Optional

from pyasic.errors import APIError
from pyasic.miners.backends import AntminerModern
from pyasic.miners.base import BaseMiner
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.web.marathon import MaraWebAPI

MARA_DATA_LOC = DataLocations(
    **{
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_brief", "brief")],
        ),
    }
)


class MaraMiner(BaseMiner):
    _web_cls = MaraWebAPI
    web: MaraWebAPI

    data_locations = MARA_DATA_LOC

    firmware = "MaraFW"

    async def _get_wattage(self, web_brief: dict = None) -> Optional[int]:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                return web_brief["power_consumption_estimated"]
            except LookupError:
                pass
