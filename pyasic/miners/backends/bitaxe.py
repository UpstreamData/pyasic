from typing import List, Optional

from pyasic import APIError
from pyasic.data import AlgoHashRate, Fan, HashBoard, HashUnit
from pyasic.miners.base import BaseMiner
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
from pyasic.web.bitaxe import BitAxeWebAPI

BITAXE_DATA_LOC = DataLocations(
    **{
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [WebAPICommand("web_system_info", "system_info")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_system_info", "system_info")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [WebAPICommand("web_system_info", "system_info")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [WebAPICommand("web_system_info", "system_info")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("web_system_info", "system_info")],
        ),
    }
)


class BitAxe(BaseMiner):
    """Handler for BitAxe"""

    web: BitAxeWebAPI
    _web_cls = BitAxeWebAPI

    data_locations = BITAXE_DATA_LOC

    async def reboot(self) -> bool:
        await self.web.restart()
        return True

    async def _get_wattage(self, web_system_info: dict = None) -> Optional[int]:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                return web_system_info["power"]
            except KeyError:
                pass

    async def _get_hashrate(
        self, web_system_info: dict = None
    ) -> Optional[AlgoHashRate]:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                return AlgoHashRate.SHA256(
                    web_system_info["hashRate"], HashUnit.SHA256.GH
                ).into(self.algo.unit.default)
            except KeyError:
                pass

    async def _get_uptime(self, web_system_info: dict = None) -> Optional[int]:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                return web_system_info["uptimeSeconds"]
            except KeyError:
                pass

    async def _get_hashboards(self, web_system_info: dict = None) -> List[HashBoard]:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                return [
                    HashBoard(
                        hashrate=AlgoHashRate.SHA256(
                            web_system_info["hashRate"], HashUnit.SHA256.GH
                        ).into(self.algo.unit.default),
                        chip_temp=web_system_info["temp"],
                        temp=web_system_info["vrTemp"],
                        chips=web_system_info["asicCount"],
                        expected_chips=self.expected_chips,
                        missing=False,
                        active=True,
                        voltage=web_system_info["voltage"],
                    )
                ]
            except KeyError:
                pass
        return []

    async def _get_fans(self, web_system_info: dict = None) -> List[Fan]:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                return [Fan(speed=web_system_info["fanrpm"])]
            except KeyError:
                pass
        return []
