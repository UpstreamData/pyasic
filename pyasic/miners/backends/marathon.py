from typing import List, Optional

from pyasic.data import Fan, HashBoard
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
from pyasic.web.marathon import MaraWebAPI

MARA_DATA_LOC = DataLocations(
    **{
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_brief", "brief")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [WebAPICommand("web_brief", "brief")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [WebAPICommand("web_brief", "brief")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [WebAPICommand("web_hashboards", "hashboards")],
        ),
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
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("web_fans", "fans")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [WebAPICommand("web_locate_miner", "locate_miner")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
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

    async def _is_mining(self, web_brief: dict = None) -> Optional[bool]:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                return web_brief["status"] == "Mining"
            except LookupError:
                pass

    async def _get_uptime(self, web_brief: dict = None) -> Optional[int]:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                return web_brief["elapsed"]
            except LookupError:
                pass

    async def _get_hashboards(self, web_hashboards: dict = None) -> List[HashBoard]:
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
                for hb in web_hashboards["hashboards"]:
                    idx = hb["index"]
                    hashboards[idx].hashrate = hb["hashrate_average"]
                    hashboards[idx].temp = round(
                        sum(hb["temperature_pcb"]) / len(hb["temperature_pcb"]), 2
                    )
                    hashboards[idx].chip_temp = round(
                        sum(hb["temperature_chip"]) / len(hb["temperature_chip"]), 2
                    )
                    hashboards[idx].chips = hb["asic_num"]
                    hashboards[idx].serial_number = hb["serial_number"]
                    hashboards[idx].missing = False
            except LookupError:
                pass
        return hashboards

    async def _get_mac(self, web_overview: dict = None) -> Optional[str]:
        if web_overview is None:
            try:
                web_overview = await self.web.overview()
            except APIError:
                pass

        if web_overview is not None:
            try:
                return web_overview["mac"].upper()
            except LookupError:
                pass

    async def _get_fw_ver(self, web_overview: dict = None) -> Optional[str]:
        if web_overview is None:
            try:
                web_overview = await self.web.overview()
            except APIError:
                pass

        if web_overview is not None:
            try:
                return web_overview["version_firmware"].upper()
            except LookupError:
                pass

    async def _get_hostname(self, web_network_config: dict = None) -> Optional[str]:
        if web_network_config is None:
            try:
                web_network_config = await self.web.get_network_config()
            except APIError:
                pass

        if web_network_config is not None:
            try:
                return web_network_config["hostname"].upper()
            except LookupError:
                pass

    async def _get_hashrate(self, web_brief: dict = None) -> Optional[float]:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                return round(web_brief["hashrate_realtime"], 2)
            except LookupError:
                pass

    async def _get_fans(self, web_fans: dict = None) -> List[Fan]:
        if web_fans is None:
            try:
                web_fans = await self.web.fans()
            except APIError:
                pass

        if web_fans is not None:
            fans = []
            for n in range(self.expected_fans):
                try:
                    fans.append(Fan(web_fans["fans"][n]["current_speed"]))
                except (IndexError, KeyError):
                    pass
            return fans
        return [Fan() for _ in range(self.expected_fans)]

    async def _get_fault_light(self, web_locate_miner: dict = None) -> bool:
        if web_locate_miner is None:
            try:
                web_locate_miner = await self.web.get_locate_miner()
            except APIError:
                pass

        if web_locate_miner is not None:
            try:
                return web_locate_miner["blinking"]
            except LookupError:
                pass
        return False

    async def _get_expected_hashrate(self, web_brief: dict = None) -> Optional[float]:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                return round(web_brief["hashrate_ideal"], 2)
            except LookupError:
                pass
