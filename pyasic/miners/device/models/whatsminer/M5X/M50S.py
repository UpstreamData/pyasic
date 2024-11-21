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
from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M50SVJ10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVJ10

    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVJ20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVJ20

    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVJ30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVJ30

    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVH10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVH10

    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVH20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVH20

    expected_chips = 135
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVH30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVH30

    expected_chips = 156
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVH40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVH40

    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVH50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVH50

    expected_chips = 135
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
