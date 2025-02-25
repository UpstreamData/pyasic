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
from pyasic.data import Fan, HashBoard
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm import AlgoHashRate
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, RPCAPICommand
from pyasic.miners.device.firmware import StockFirmware
from pyasic.rpc.bfgminer import BFGMinerRPCAPI

BFGMINER_DATA_LOC = DataLocations(
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
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
    }
)


class BFGMiner(StockFirmware):
    """Base handler for BFGMiner based miners."""

    _rpc_cls = BFGMinerRPCAPI
    rpc: BFGMinerRPCAPI

    data_locations = BFGMINER_DATA_LOC

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
                self.fw_ver = rpc_version["VERSION"][0]["CompileTime"]
            except LookupError:
                pass

        return self.fw_ver

    async def _get_hashrate(self, rpc_summary: dict = None) -> Optional[AlgoHashRate]:
        # get hr from API
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return self.algo.hashrate(
                    rate=float(rpc_summary["SUMMARY"][0]["MHS 20s"]),
                    unit=self.algo.unit.MH,
                ).into(self.algo.unit.default)
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_hashboards(self, rpc_stats: dict = None) -> List[HashBoard]:
        hashboards = []

        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                board_offset = -1
                boards = rpc_stats["STATS"]
                if len(boards) > 1:
                    for board_num in range(1, 16, 5):
                        for _b_num in range(5):
                            b = boards[1].get(f"chain_acn{board_num + _b_num}")

                            if b and not b == 0 and board_offset == -1:
                                board_offset = board_num
                    if board_offset == -1:
                        board_offset = 1

                    for i in range(
                        board_offset, board_offset + self.expected_hashboards
                    ):
                        hashboard = HashBoard(
                            slot=i - board_offset, expected_chips=self.expected_chips
                        )

                        chip_temp = boards[1].get(f"temp{i}")
                        if chip_temp:
                            hashboard.chip_temp = round(chip_temp)

                        temp = boards[1].get(f"temp2_{i}")
                        if temp:
                            hashboard.temp = round(temp)

                        hashrate = boards[1].get(f"chain_rate{i}")
                        if hashrate:
                            hashboard.hashrate = self.algo.hashrate(
                                rate=float(hashrate), unit=self.algo.unit.GH
                            ).into(self.algo.unit.default)

                        chips = boards[1].get(f"chain_acn{i}")
                        if chips:
                            hashboard.chips = chips
                            hashboard.missing = False
                        if (not chips) or (not chips > 0):
                            hashboard.missing = True
                        hashboards.append(hashboard)
            except (LookupError, ValueError, TypeError):
                pass

        return hashboards

    async def _get_fans(self, rpc_stats: dict = None) -> List[Fan]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        fans_data = [None, None, None, None]
        if rpc_stats is not None:
            try:
                fan_offset = -1

                for fan_num in range(0, 8, 4):
                    for _f_num in range(4):
                        f = rpc_stats["STATS"][1].get(f"fan{fan_num + _f_num}", 0)
                        if not f == 0 and fan_offset == -1:
                            fan_offset = fan_num
                if fan_offset == -1:
                    fan_offset = 1

                for fan in range(self.expected_fans):
                    fans_data[fan] = rpc_stats["STATS"][1].get(
                        f"fan{fan_offset+fan}", 0
                    )
            except LookupError:
                pass
        fans = [Fan(speed=d) if d else Fan() for d in fans_data]

        return fans

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

    async def _get_expected_hashrate(
        self, rpc_stats: dict = None
    ) -> Optional[AlgoHashRate]:
        # X19 method, not sure compatibility
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                expected_rate = rpc_stats["STATS"][1]["total_rateideal"]
                try:
                    rate_unit = rpc_stats["STATS"][1]["rate_unit"]
                except KeyError:
                    rate_unit = "GH"
                return self.algo.hashrate(
                    rate=float(expected_rate), unit=self.algo.unit.from_str(rate_unit)
                ).into(self.algo.unit.default)
            except LookupError:
                pass
