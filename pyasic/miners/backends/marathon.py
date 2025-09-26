from pyasic import MinerConfig
from pyasic.config import MiningModeConfig
from pyasic.data import Fan, HashBoard
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm import AlgoHashRateType
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
from pyasic.miners.device.firmware import MaraFirmware
from pyasic.misc import merge_dicts
from pyasic.rpc.marathon import MaraRPCAPI
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
        return res.get("blinking") is False

    async def fault_light_on(self) -> bool:
        res = await self.web.set_locate_miner(blinking=True)
        return res.get("blinking") is True

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

    async def _get_wattage(self, web_brief: dict | None = None) -> int | None:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass
        return None

        if web_brief is not None:
            try:
                return round(web_brief["power_consumption_estimated"])
            except LookupError:
                pass

    async def _is_mining(self, web_brief: dict | None = None) -> bool | None:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass
        return None

        if web_brief is not None:
            try:
                return web_brief["status"] == "Mining"
            except LookupError:
                pass

    async def _get_uptime(self, web_brief: dict | None = None) -> int | None:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass
        return None

        if web_brief is not None:
            try:
                return web_brief["elapsed"]
            except LookupError:
                pass

    async def _get_hashboards(
        self, web_hashboards: dict | None = None
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
                for hb in web_hashboards["hashboards"]:
                    idx = hb["index"]
                    hashboards[idx].hashrate = self.algo.hashrate(
                        rate=float(hb["hashrate_average"]),
                        unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                    ).into(
                        self.algo.unit.default  # type: ignore[attr-defined]
                    )
                    hashboards[idx].temp = round(
                        sum(hb["temperature_pcb"]) / len(hb["temperature_pcb"])
                    )
                    hashboards[idx].chip_temp = round(
                        sum(hb["temperature_chip"]) / len(hb["temperature_chip"])
                    )
                    hashboards[idx].chips = hb["asic_num"]
                    hashboards[idx].serial_number = hb["serial_number"]
                    hashboards[idx].missing = False
            except LookupError:
                pass
        return hashboards

    async def _get_mac(self, web_overview: dict | None = None) -> str | None:
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
        return None

    async def _get_fw_ver(self, web_overview: dict | None = None) -> str | None:
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
        return None

    async def _get_hostname(self, web_network_config: dict | None = None) -> str | None:
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
        return None

    async def _get_hashrate(
        self, web_brief: dict | None = None
    ) -> AlgoHashRateType | None:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                return self.algo.hashrate(
                    rate=float(web_brief["hashrate_realtime"]),
                    unit=self.algo.unit.TH,  # type: ignore[attr-defined]
                ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except LookupError:
                pass
        return None

    async def _get_fans(self, web_fans: dict | None = None) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if web_fans is None:
            try:
                web_fans = await self.web.fans()
            except APIError:
                pass

        if web_fans is not None:
            fans = []
            for n in range(self.expected_fans):
                try:
                    fans.append(Fan(speed=web_fans["fans"][n]["current_speed"]))
                except (IndexError, KeyError):
                    pass
            return fans
        return [Fan() for _ in range(self.expected_fans)]

    async def _get_fault_light(self, web_locate_miner: dict | None = None) -> bool:
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

    async def _get_expected_hashrate(
        self, web_brief: dict | None = None
    ) -> AlgoHashRateType | None:
        if web_brief is None:
            try:
                web_brief = await self.web.brief()
            except APIError:
                pass

        if web_brief is not None:
            try:
                return self.algo.hashrate(
                    rate=float(web_brief["hashrate_ideal"]),
                    unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except LookupError:
                pass
        return None

    async def _get_wattage_limit(
        self, web_miner_config: dict | None = None
    ) -> int | None:
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
        return None

    async def _get_pools(self, web_pools: list | None = None) -> list[PoolMetrics]:
        if web_pools is None:
            try:
                web_pools = await self.web.pools()
            except APIError:
                return []

        active_pool_index = None
        highest_priority = float("inf")

        for pool_info in web_pools:
            if (
                pool_info.get("status") == "Alive"
                and pool_info.get("priority", float("inf")) < highest_priority
            ):
                highest_priority = pool_info["priority"]
                active_pool_index = pool_info["index"]

        pools_data = []
        if web_pools is not None:
            try:
                for pool_info in web_pools:
                    url = pool_info.get("url")
                    pool_url = PoolUrl.from_str(url) if url else None
                    pool_data = PoolMetrics(
                        accepted=pool_info.get("accepted"),
                        rejected=pool_info.get("rejected"),
                        get_failures=pool_info.get("stale"),
                        remote_failures=pool_info.get("discarded"),
                        active=pool_info.get("index") == active_pool_index,
                        alive=pool_info.get("status") == "Alive",
                        url=pool_url,
                        user=pool_info.get("user"),
                        index=pool_info.get("index"),
                    )
                    pools_data.append(pool_data)
            except LookupError:
                pass
        return pools_data
