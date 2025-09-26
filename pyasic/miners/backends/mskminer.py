from pyasic import APIError
from pyasic.device.algorithm import AlgoHashRateType
from pyasic.miners.backends import BMMiner
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.web.mskminer import MSKMinerWebAPI

MSKMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_info_v1", "info_v1")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
    }
)


class MSKMiner(BMMiner):
    """Handler for MSKMiner"""

    data_locations = MSKMINER_DATA_LOC

    web: MSKMinerWebAPI
    _web_cls = MSKMinerWebAPI

    async def _get_hashrate(
        self, rpc_stats: dict | None = None
    ) -> AlgoHashRateType | None:
        # get hr from API
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                return self.algo.hashrate(
                    rate=float(rpc_stats["STATS"][0]["total_rate"]),
                    unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                ).into(
                    self.algo.unit.default  # type: ignore[attr-defined]
                )
            except (LookupError, ValueError, TypeError):
                pass
        return None

    async def _get_wattage(self, rpc_stats: dict | None = None) -> int | None:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                return rpc_stats["STATS"][0]["total_power"]
            except (LookupError, ValueError, TypeError):
                pass
        return None

    async def _get_mac(self, web_info_v1: dict | None = None) -> str | None:
        if web_info_v1 is None:
            try:
                web_info_v1 = await self.web.info_v1()
            except APIError:
                pass

        if web_info_v1 is not None:
            try:
                return web_info_v1["network_info"]["result"]["macaddr"].upper()
            except (LookupError, ValueError, TypeError):
                pass
        return None
