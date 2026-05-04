"""Backend support for Fluminer stock firmware miners."""

from pyasic import MinerConfig
from pyasic.config.pools import Pool, PoolConfig, PoolGroup
from pyasic.data import Fan, HashBoard
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm import AlgoHashRateType
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
from pyasic.miners.device.firmware import StockFirmware
from pyasic.web.fluminer import FluminerWebAPI

FLUMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.SERIAL_NUMBER): DataFunction(
            "_get_serial_number",
            [WebAPICommand("web_overview", "api/overview")],
        ),
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_overview", "api/overview")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_overview", "api/overview")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_overview", "api/overview")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [WebAPICommand("web_summary", "api/summary")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [WebAPICommand("web_summary", "api/summary")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_summary", "api/summary")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("web_summary", "api/summary")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [WebAPICommand("web_summary", "api/summary")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [WebAPICommand("web_summary", "api/summary")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [
                WebAPICommand("web_summary", "api/summary"),
                WebAPICommand("web_pools", "api/getPools"),
            ],
        ),
    }
)


class Fluminer(StockFirmware):
    _web_cls = FluminerWebAPI
    web: FluminerWebAPI

    data_locations = FLUMINER_DATA_LOC

    async def get_config(self) -> MinerConfig:
        try:
            web_pools = await self.web.pools()
        except APIError:
            return MinerConfig()

        pools = []
        for pool in self._get_configured_pools(web_pools):
            if pool.get("url"):
                pools.append(
                    Pool(
                        url=pool["url"],
                        user=pool.get("user", ""),
                        password=pool.get("pass", ""),
                    )
                )
        return MinerConfig(pools=PoolConfig(groups=[PoolGroup(pools=pools)]))

    async def _get_serial_number(self, web_overview: dict | None = None) -> str | None:
        miner_info = await self._get_miner_info(web_overview)
        return miner_info.get("sn") or None

    async def _get_mac(self, web_overview: dict | None = None) -> str | None:
        miner_info = await self._get_miner_info(web_overview)
        mac = miner_info.get("macAddress") or miner_info.get("wifiMacAddress")
        if isinstance(mac, str) and mac:
            return mac.upper()
        return None

    async def _get_fw_ver(self, web_overview: dict | None = None) -> str | None:
        miner_info = await self._get_miner_info(web_overview)
        return miner_info.get("minerVersion") or None

    async def _get_hostname(self, web_overview: dict | None = None) -> str | None:
        miner_info = await self._get_miner_info(web_overview)
        sn = miner_info.get("sn")
        if sn:
            return f"fluminer-{sn}"
        return None

    async def _get_hashrate(
        self, web_summary: dict | None = None
    ) -> AlgoHashRateType | None:
        summary = await self._get_summary(web_summary)
        return self._hashrate_from_gh(summary.get("hrt"))

    async def _get_hashboards(self, web_summary: dict | None = None) -> list[HashBoard]:
        if self.expected_hashboards is None:
            return []

        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]
        summary = await self._get_summary(web_summary)
        if not summary:
            return hashboards

        hashrate = self._hashrate_from_gh(summary.get("hrt"))
        temps = self._split_ints(summary.get("temp"))

        hashboards[0].hashrate = hashrate
        hashboards[0].temp = temps[0] if len(temps) > 0 else None
        hashboards[0].chip_temp = temps[1] if len(temps) > 1 else None
        hashboards[0].missing = False
        hashboards[0].active = summary.get("status") == "OK"
        hashboards[0].voltage = self._float_or_none(summary.get("voltage"))
        return hashboards

    async def _get_wattage(self, web_summary: dict | None = None) -> int | None:
        summary = await self._get_summary(web_summary)
        wattage = self._float_or_none(summary.get("power"))
        return round(wattage) if wattage is not None else None

    async def _get_voltage(self, web_summary: dict | None = None) -> float | None:
        summary = await self._get_summary(web_summary)
        return self._float_or_none(summary.get("voltage"))

    async def _get_fans(self, web_summary: dict | None = None) -> list[Fan]:
        summary = await self._get_summary(web_summary)
        speeds = self._split_ints(summary.get("fan"))
        if self.expected_fans is not None:
            speeds = speeds[: self.expected_fans]
            return [
                Fan(speed=speeds[i]) if i < len(speeds) else Fan()
                for i in range(self.expected_fans)
            ]
        return [Fan(speed=speed) for speed in speeds]

    async def _is_mining(self, web_summary: dict | None = None) -> bool | None:
        summary = await self._get_summary(web_summary)
        return summary.get("status") == "OK" and self._float_or_none(
            summary.get("hrt")
        ) not in (None, 0.0)

    async def _get_uptime(self, web_summary: dict | None = None) -> int | None:
        summary = await self._get_summary(web_summary)
        uptime = summary.get("uptime")
        if uptime is None:
            return None
        try:
            return int(uptime)
        except (TypeError, ValueError):
            return None

    async def _get_pools(
        self,
        web_summary: dict | None = None,
        web_pools: dict | None = None,
    ) -> list[PoolMetrics]:
        summary = await self._get_summary(web_summary)
        if web_pools is None:
            try:
                web_pools = await self.web.pools()
            except APIError:
                web_pools = None

        pools = []
        configured_pools = self._get_configured_pools(web_pools)
        for idx, pool in enumerate(configured_pools):
            url = pool.get("url")
            if not url:
                continue
            pool_url = self._pool_url_from_str(url)
            if pool_url is None:
                continue
            active = self._is_active_pool(summary, url)
            pools.append(
                PoolMetrics(
                    accepted=self._int_or_none(summary.get("acc")) if active else None,
                    rejected=self._int_or_none(summary.get("rej")) if active else None,
                    active=active,
                    alive=summary.get("poolAlive") == "1" if active else None,
                    url=pool_url,
                    user=pool.get("user"),
                    index=idx,
                )
            )
        return pools

    async def _get_miner_info(self, web_overview: dict | None = None) -> dict:
        if web_overview is None:
            try:
                web_overview = await self.web.overview()
            except APIError:
                return {}
        data = web_overview.get("data") if isinstance(web_overview, dict) else None
        if not isinstance(data, dict):
            return {}
        miner_info = data.get("minerInfo")
        if isinstance(miner_info, dict):
            return miner_info
        return {}

    async def _get_summary(self, web_summary: dict | None = None) -> dict:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                return {}
        data = web_summary.get("data") if isinstance(web_summary, dict) else None
        if not isinstance(data, dict):
            return {}
        summaries = data.get("summary")
        if (
            isinstance(summaries, list)
            and len(summaries) > 0
            and isinstance(summaries[0], dict)
        ):
            return summaries[0]
        return {}

    def _hashrate_from_gh(self, value: object) -> AlgoHashRateType | None:
        hashrate = self._float_or_none(value)
        if hashrate is None:
            return None
        return self.algo.hashrate(
            rate=hashrate,
            unit=self.algo.unit.GH,  # type: ignore[attr-defined]
        ).into(
            self.algo.unit.default  # type: ignore[attr-defined]
        )

    @staticmethod
    def _split_ints(value: object) -> list[int]:
        if not isinstance(value, str):
            return []
        values = []
        for item in value.split("|"):
            try:
                values.append(round(float(item)))
            except ValueError:
                continue
        return values

    @staticmethod
    def _float_or_none(value: object) -> float | None:
        if not isinstance(value, (float, int, str)):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _int_or_none(value: object) -> int | None:
        if not isinstance(value, (float, int, str)):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _get_configured_pools(web_pools: dict | None) -> list[dict]:
        data = web_pools.get("data") if isinstance(web_pools, dict) else None
        if not isinstance(data, dict):
            return []
        pools = data.get("pools")
        if not isinstance(pools, list):
            return []
        return [pool for pool in pools if isinstance(pool, dict)]

    @staticmethod
    def _pool_url_from_str(url: str) -> PoolUrl | None:
        try:
            return PoolUrl.from_str(url)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _is_active_pool(cls, summary: dict, url: str) -> bool:
        pool_host = summary.get("pool")
        pool_port = summary.get("port")
        pool_url = cls._pool_url_from_str(url)
        return (
            pool_url is not None
            and isinstance(pool_host, str)
            and pool_url.host == pool_host
            and (pool_port is None or str(pool_url.port) == str(pool_port))
        )
