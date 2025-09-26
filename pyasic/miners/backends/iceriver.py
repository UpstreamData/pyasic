from pyasic import MinerConfig
from pyasic.data import Fan, HashBoard
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm import AlgoHashRateType, MinerAlgo
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

    async def _get_fans(self, web_userpanel: dict | None = None) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                return []

        if web_userpanel is not None:
            try:
                return [
                    Fan(speed=spd) for spd in web_userpanel["userpanel"]["data"]["fans"]
                ]
            except (LookupError, ValueError, TypeError):
                pass
        return []

    async def _get_mac(self, web_userpanel: dict | None = None) -> str | None:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                return None

        if web_userpanel is not None:
            try:
                return (
                    web_userpanel["userpanel"]["data"]["mac"].upper().replace("-", ":")
                )
            except (LookupError, ValueError, TypeError):
                pass
        return None

    async def _get_hostname(self, web_userpanel: dict | None = None) -> str | None:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                return None

        if web_userpanel is not None:
            try:
                return web_userpanel["userpanel"]["data"]["host"]
            except (LookupError, ValueError, TypeError):
                pass
        return None

    async def _get_hashrate(
        self, web_userpanel: dict | None = None
    ) -> AlgoHashRateType | None:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                return None

        if web_userpanel is not None:
            try:
                base_unit = web_userpanel["userpanel"]["data"]["unit"]
                return self.algo.hashrate(
                    rate=float(
                        web_userpanel["userpanel"]["data"]["rtpow"].replace(
                            base_unit, ""
                        )
                    ),
                    unit=MinerAlgo.SHA256.unit.from_str(base_unit + "H"),
                ).into(MinerAlgo.SHA256.unit.default)
            except (LookupError, ValueError, TypeError):
                pass
        return None

    async def _get_fault_light(self, web_userpanel: dict | None = None) -> bool:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        if web_userpanel is not None:
            try:
                return web_userpanel["userpanel"]["data"]["locate"]
            except (LookupError, ValueError, TypeError):
                pass
        return False

    async def _is_mining(self, web_userpanel: dict | None = None) -> bool | None:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                return False

        if web_userpanel is not None:
            try:
                return web_userpanel["userpanel"]["data"]["powstate"]
            except (LookupError, ValueError, TypeError):
                pass
        return False

    async def _get_hashboards(
        self, web_userpanel: dict | None = None
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
                for board in web_userpanel["userpanel"]["data"]["boards"]:
                    idx = int(board["no"] - 1)
                    hb_list[idx].chip_temp = round(board["outtmp"])
                    hb_list[idx].temp = round(board["intmp"])
                    hb_list[idx].hashrate = self.algo.hashrate(
                        rate=float(board["rtpow"].replace("G", "")),
                        unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                    ).into(
                        self.algo.unit.default  # type: ignore[attr-defined]
                    )
                    hb_list[idx].chips = int(board["chipnum"])
                    hb_list[idx].missing = False
            except LookupError:
                pass
        return hb_list

    async def _get_uptime(self, web_userpanel: dict | None = None) -> int | None:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        if web_userpanel is not None:
            try:
                runtime = web_userpanel["userpanel"]["data"]["runtime"]
                days, hours, minutes, seconds = runtime.split(":")
                return (
                    (int(days) * 24 * 60 * 60)
                    + (int(hours) * 60 * 60)
                    + (int(minutes) * 60)
                    + int(seconds)
                )
            except (LookupError, ValueError, TypeError):
                pass
        return None

    async def _get_pools(self, web_userpanel: dict | None = None) -> list[PoolMetrics]:
        if web_userpanel is None:
            try:
                web_userpanel = await self.web.userpanel()
            except APIError:
                pass

        pools_data = []
        if web_userpanel is not None:
            try:
                pools = web_userpanel["userpanel"]["data"]["pools"]
                for pool_info in pools:
                    pool_num = pool_info.get("no")
                    if pool_num is not None:
                        pool_num = int(pool_num)
                    if pool_info["addr"] == "":
                        continue
                    url = pool_info.get("addr")
                    pool_url = PoolUrl.from_str(url) if url else None
                    pool_data = PoolMetrics(
                        accepted=pool_info.get("accepted"),
                        rejected=pool_info.get("rejected"),
                        active=pool_info.get("connect"),
                        alive=int(pool_info.get("state", 0)) == 1,
                        url=pool_url,
                        user=pool_info.get("user"),
                        index=pool_num,
                    )
                    pools_data.append(pool_data)
            except LookupError:
                pass
        return pools_data
