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

from pyasic import settings
from pyasic.data import HashBoard
from pyasic.miners.backends import BMMiner
from pyasic.miners.base import DataFunction, DataLocations, DataOptions, RPCAPICommand

HIVEON_DATA_LOC = DataLocations(
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
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction(
            "_get_env_temp",
            [RPCAPICommand("api_stats", "stats")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
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


class Hiveon(BMMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver)
        self.pwd = settings.get("default_hive_password", "admin")
        # static data
        self.api_type = "Hiveon"
        # data gathering locations
        self.data_locations = HIVEON_DATA_LOC

    async def _get_hashboards(self, api_stats: dict = None) -> List[HashBoard]:
        pass

    async def _get_wattage(self, api_stats: dict = None) -> Optional[int]:
        pass

    async def _get_env_temp(self, api_stats: dict = None) -> Optional[float]:
        pass
