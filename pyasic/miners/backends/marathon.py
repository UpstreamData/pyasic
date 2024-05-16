from typing import List, Optional

from pyasic import MinerConfig
from pyasic.config import MiningModeConfig
from pyasic.data import AlgoHashRate, Fan, HashBoard, HashUnit
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
from pyasic.miners.device.firmware import MaraFirmware
from pyasic.misc import merge_dicts
from pyasic.web.marathon import MaraWebAPI

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
    }
)


class MaraMiner(MaraFirmware):
    _web_cls = MaraWebAPI
    web: MaraWebAPI

    data_locations = MARA_DATA_LOC

    async def fault_light_off(self) -> bool:
        res = await self.web.set_locate_miner(blinking=False)
        return res.get("blinking") is False

    async def fault_light_on(self) -> bool:
        res = await self.web.set_locate_miner(blinking=True)
        return res.get("blinking") is True

    async def get_config(self) -> MinerConfig:
        data = await self.web.get_miner_config()
        if data:
            self.config = MinerConfig.from_mara(data)
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        data = await self.web.get_miner_config()
        cfg_data = config.as_mara(user_suffix=user_suffix)
        merged_cfg = merge_dicts(data, cfg_data)
        await self.web.set_miner_config(**merged_cfg)

    async def set_power_limit(self, wattage: int) -> bool:
        cfg = await self.get_config()
        cfg.mining_mode = MiningModeConfig.power_tuning(wattage)
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

    async def _get_wattage(self, web_brief: dict = None) -> Optional[int]:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                return round(web_brief["power_consumption_estimated"])
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
                    hashboards[idx].hashrate = AlgoHashRate.SHA256(
                        hb["hashrate_average"], HashUnit.SHA256.GH
                    ).into(self.algo.unit.default)
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
                return web_overview["version_firmware"]
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
                return web_network_config["hostname"]
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
                return AlgoHashRate.SHA256(
                    web_brief["hashrate_realtime"], HashUnit.SHA256.TH
                ).into(self.algo.unit.default)
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
                return AlgoHashRate.SHA256(
                    web_brief["hashrate_ideal"], HashUnit.SHA256.GH
                ).int(self.algo.unit.default)
            except LookupError:
                pass

    async def _get_wattage_limit(
        self, web_miner_config: dict = None
    ) -> Optional[float]:
        if web_miner_config is None:
            try:
                web_miner_config = await self.web.get_miner_config()
            except APIError:
                pass

        if web_miner_config is not None:
            try:
                return web_miner_config["mode"]["concorde"]["power-target"]
            except LookupError:
                pass
