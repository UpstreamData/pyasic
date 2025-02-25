# ------------------------------------------------------------------------------
#  Copyright 2024 Upstream Data Inc                                            -
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
from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import IceRiverMake


class KS3(IceRiverMake):
    raw_model = MinerModel.ICERIVER.KS3

    expected_fans = 4
    expected_hashboards = 3
    algo = MinerAlgo.KHEAVYHASH


class KS3L(IceRiverMake):
    raw_model = MinerModel.ICERIVER.KS3L

    expected_fans = 4
    expected_hashboards = 3
    algo = MinerAlgo.KHEAVYHASH


class KS3M(IceRiverMake):
    raw_model = MinerModel.ICERIVER.KS3M

    expected_fans = 4
    expected_chips = 18
    expected_hashboards = 3
    algo = MinerAlgo.KHEAVYHASH
