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
from pyasic.errors import APIError
from pyasic.miners.base import (
    BaseMiner,
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
)
from pyasic.rpc.bmminer import BMMinerRPCAPI

BMMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("api_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [RPCAPICommand("api_version", "version")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("api_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("api_stats", "stats")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("api_stats", "stats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("api_stats", "stats")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("api_stats", "stats")],
        ),
    }
)


class BMMiner(BaseMiner):
    """Base handler for BMMiner based miners."""

    _api_cls = BMMinerRPCAPI
    api: BMMinerRPCAPI

    data_locations = BMMINER_DATA_LOC

    async def get_config(self) -> MinerConfig:
        # get pool data
        try:
            pools = await self.api.pools()
        except APIError:
            return self.config

        self.config = MinerConfig.from_api(pools)
        return self.config

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_api_ver(self, api_version: dict = None) -> Optional[str]:
        if api_version is None:
            try:
                api_version = await self.api.version()
            except APIError:
                pass

        if api_version is not None:
            try:
                self.api_ver = api_version["VERSION"][0]["API"]
            except LookupError:
                pass

        return self.api_ver

    async def _get_fw_ver(self, api_version: dict = None) -> Optional[str]:
        if api_version is None:
            try:
                api_version = await self.api.version()
            except APIError:
                pass

        if api_version is not None:
            try:
                self.fw_ver = api_version["VERSION"][0]["CompileTime"]
            except LookupError:
                pass

        return self.fw_ver

    async def _get_hashrate(self, api_summary: dict = None) -> Optional[float]:
        # get hr from API
        if api_summary is None:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary is not None:
            try:
                return round(float(api_summary["SUMMARY"][0]["GHS 5s"] / 1000), 2)
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_hashboards(self, api_stats: dict = None) -> List[HashBoard]:
        hashboards = []

        if api_stats is None:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats is not None:
            try:
                board_offset = -1
                boards = api_stats["STATS"]
                if len(boards) > 1:
                    for board_num in range(1, 16, 5):
                        for _b_num in range(5):
                            b = boards[1].get(f"chain_acn{board_num + _b_num}")

                            if b and not b == 0 and board_offset == -1:
                                board_offset = board_num
                    if board_offset == -1:
                        board_offset = 1

                    real_slots = []

                    for i in range(board_offset, board_offset + 4):
                        try:
                            key = f"chain_acs{i}"
                            if boards[1].get(key, "") != "":
                                real_slots.append(i)
                        except LookupError:
                            pass

                    if len(real_slots) < 3:
                        real_slots = list(
                            range(board_offset, board_offset + self.expected_hashboards)
                        )

                    for i in real_slots:
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
                            hashboard.hashrate = round(float(hashrate) / 1000, 2)

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

    async def _get_fans(self, api_stats: dict = None) -> List[Fan]:
        if api_stats is None:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        fans = [Fan() for _ in range(self.expected_fans)]
        if api_stats is not None:
            try:
                fan_offset = -1

                for fan_num in range(1, 8, 4):
                    for _f_num in range(4):
                        f = api_stats["STATS"][1].get(f"fan{fan_num + _f_num}", 0)
                        if f and not f == 0 and fan_offset == -1:
                            fan_offset = fan_num
                if fan_offset == -1:
                    fan_offset = 1

                for fan in range(self.expected_fans):
                    fans[fan].speed = api_stats["STATS"][1].get(
                        f"fan{fan_offset+fan}", 0
                    )
            except LookupError:
                pass

        return fans

    async def _get_expected_hashrate(self, api_stats: dict = None) -> Optional[float]:
        # X19 method, not sure compatibility
        if api_stats is None:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats is not None:
            try:
                expected_rate = api_stats["STATS"][1]["total_rateideal"]
                try:
                    rate_unit = api_stats["STATS"][1]["rate_unit"]
                except KeyError:
                    rate_unit = "GH"
                if rate_unit == "GH":
                    return round(expected_rate / 1000, 2)
                if rate_unit == "MH":
                    return round(expected_rate / 1000000, 2)
                else:
                    return round(expected_rate, 2)
            except LookupError:
                pass

    async def _get_uptime(self, api_stats: dict = None) -> Optional[int]:
        if api_stats is None:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats is not None:
            try:
                return int(api_stats["STATS"][1]["Elapsed"])
            except LookupError:
                pass
