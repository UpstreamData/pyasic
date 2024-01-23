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

from pyasic.miners.base import BaseMiner, DataLocations
from pyasic.rpc.gcminer import GCMinerRPCAPI
from pyasic.web.auradine import FluxWebAPI

AURADINE_DATA_LOC = DataLocations(**{})


class Auradine(BaseMiner):
    """Base handler for Auradine miners"""

    _api_cls = GCMinerRPCAPI
    api: GCMinerRPCAPI
    _web_cls = FluxWebAPI
    web: FluxWebAPI

    data_locations = AURADINE_DATA_LOC
