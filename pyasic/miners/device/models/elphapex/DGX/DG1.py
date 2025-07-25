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
from pyasic.miners.device.makes import ElphapexMake


class DG1(ElphapexMake):
    raw_model = MinerModel.ELPHAPEX.DG1

    expected_chips = 144
    expected_hashboards = 4
    expected_fans = 4
    algo = MinerAlgo.SCRYPT


class DG1Plus(ElphapexMake):
    raw_model = MinerModel.ELPHAPEX.DG1Plus

    expected_chips = 204
    expected_hashboards = 4
    expected_fans = 4
    algo = MinerAlgo.SCRYPT


class DG1Home(ElphapexMake):
    raw_model = MinerModel.ELPHAPEX.DG1Home

    expected_chips = 120
    expected_hashboards = 4
    expected_fans = 4
    algo = MinerAlgo.SCRYPT
