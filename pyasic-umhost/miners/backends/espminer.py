from typing import List, Optional

from pyasic import APIError, MinerConfig
from pyasic.data import Fan, HashBoard
from pyasic.device.algorithm import AlgoHashRate
from pyasic.device.firmware import MinerFirmware
from pyasic.miners.base import BaseMiner
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
from pyasic.web.espminer import ESPMinerWebAPI

ESPMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_system_info", "system/info")],
        ),
    }
)


class ESPMiner(BaseMiner):
    """Handler for ESPMiner"""

    web: ESPMinerWebAPI
    _web_cls = ESPMinerWebAPI

    firmware = MinerFirmware.STOCK

    data_locations = ESPMINER_DATA_LOC

    async def reboot(self) -> bool:
        await self.web.restart()
        return True

    async def get_config(self) -> MinerConfig:
        web_system_info = await self.web.system_info()
        return MinerConfig.from_espminer(web_system_info)

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        await self.web.update_settings(**config.as_espminer())

    async def _get_wattage(self, web_system_info: dict = None) -> Optional[int]:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass
        if web_system_info is not None:
            try:
                return round(web_system_info["power"])
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
                return self.algo.hashrate(
                    rate=float(web_system_info["hashRate"]), unit=self.algo.unit.GH
                ).into(self.algo.unit.default)
            except KeyError:
                pass

    async def _get_expected_hashrate(
        self, web_system_info: dict = None
    ) -> Optional[AlgoHashRate]:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                expected_hashrate = (
                    web_system_info.get("smallCoreCount")
                    * web_system_info.get("asicCount")
                    * web_system_info.get("frequency")
                )

                return self.algo.hashrate(
                    rate=float(expected_hashrate), unit=self.algo.unit.MH
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
                        hashrate=self.algo.hashrate(
                            rate=float(web_system_info["hashRate"]),
                            unit=self.algo.unit.GH,
                        ).into(self.algo.unit.default),
                        chip_temp=web_system_info.get("temp"),
                        temp=web_system_info.get("vrTemp"),
                        chips=web_system_info.get("asicCount", 1),
                        expected_chips=self.expected_chips,
                        missing=False,
                        active=True,
                        voltage=web_system_info.get("voltage"),
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

    async def _get_hostname(self, web_system_info: dict = None) -> Optional[str]:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                return web_system_info["hostname"]
            except KeyError:
                pass

    async def _get_api_ver(self, web_system_info: dict = None) -> Optional[str]:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                return web_system_info["version"]
            except KeyError:
                pass

    async def _get_fw_ver(self, web_system_info: dict = None) -> Optional[str]:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                return web_system_info["version"]
            except KeyError:
                pass

    async def _get_mac(self, web_system_info: dict = None) -> Optional[str]:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                return web_system_info["macAddr"].upper()
            except KeyError:
                pass
