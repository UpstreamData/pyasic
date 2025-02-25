# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------

from typing import List, Optional

from pyasic.config import MinerConfig
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm import AlgoHashRate
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, RPCAPICommand
from pyasic.miners.device.firmware import StockFirmware
from pyasic.rpc.cgminer import CGMinerRPCAPI

CGMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
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


class CGMiner(StockFirmware):
    """Base handler for CGMiner based miners"""

    _rpc_cls = CGMinerRPCAPI
    rpc: CGMinerRPCAPI

    data_locations = CGMINER_DATA_LOC

    async def get_config(self) -> MinerConfig:
        # get pool data
        try:
            pools = await self.rpc.pools()
        except APIError:
            return self.config

        self.config = MinerConfig.from_api(pools)
        return self.config

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_api_ver(self, rpc_version: dict = None) -> Optional[str]:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                pass

        if rpc_version is not None:
            try:
                self.api_ver = rpc_version["VERSION"][0]["API"]
            except LookupError:
                pass

        return self.api_ver

    async def _get_fw_ver(self, rpc_version: dict = None) -> Optional[str]:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                pass

        if rpc_version is not None:
            try:
                self.fw_ver = rpc_version["VERSION"][0]["CGMiner"]
            except LookupError:
                pass

        return self.fw_ver

    async def _get_hashrate(self, rpc_summary: dict = None) -> Optional[AlgoHashRate]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return self.algo.hashrate(
                    rate=float(rpc_summary["SUMMARY"][0]["GHS 5s"]),
                    unit=self.algo.unit.GH,
                ).into(self.algo.unit.default)
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_uptime(self, rpc_stats: dict = None) -> Optional[int]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                return int(rpc_stats["STATS"][1]["Elapsed"])
            except LookupError:
                pass

    async def _get_pools(self, rpc_pools: dict = None) -> List[PoolMetrics]:
        if rpc_pools is None:
            try:
                rpc_pools = await self.rpc.pools()
            except APIError:
                pass

        pools_data = []
        if rpc_pools is not None:
            try:
                pools = rpc_pools.get("POOLS", [])
                for pool_info in pools:
                    url = pool_info.get("URL")
                    pool_url = PoolUrl.from_str(url) if url else None
                    pool_data = PoolMetrics(
                        accepted=pool_info.get("Accepted"),
                        rejected=pool_info.get("Rejected"),
                        get_failures=pool_info.get("Get Failures"),
                        remote_failures=pool_info.get("Remote Failures"),
                        active=pool_info.get("Stratum Active"),
                        alive=pool_info.get("Status") == "Alive",
                        url=pool_url,
                        user=pool_info.get("User"),
                        index=pool_info.get("POOL"),
                    )
                    pools_data.append(pool_data)
            except LookupError:
                pass
        return pools_data
