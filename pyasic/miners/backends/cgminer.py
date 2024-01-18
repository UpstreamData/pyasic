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

from typing import Optional

from pyasic.config import MinerConfig
from pyasic.errors import APIError
from pyasic.miners.base import (
    BaseMiner,
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
)
from pyasic.rpc.cgminer import CGMinerRPCAPI

CGMINER_DATA_LOC = DataLocations(
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


class CGMiner(BaseMiner):
    """Base handler for CGMiner based miners"""

    _api_cls = CGMinerRPCAPI
    api: CGMinerRPCAPI

    data_locations = CGMINER_DATA_LOC

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
                self.fw_ver = api_version["VERSION"][0]["CGMiner"]
            except LookupError:
                pass

        return self.fw_ver

    async def _get_hashrate(self, api_summary: dict = None) -> Optional[float]:
        if api_summary is None:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary is not None:
            try:
                return round(
                    float(float(api_summary["SUMMARY"][0]["GHS 5s"]) / 1000), 2
                )
            except (LookupError, ValueError, TypeError):
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
