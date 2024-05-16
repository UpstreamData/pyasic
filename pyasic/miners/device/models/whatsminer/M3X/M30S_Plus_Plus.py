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
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M30SPlusPlusV10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusV10
    expected_hashboards = 4
    expected_chips = 255


class M30SPlusPlusV20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusV20
    expected_hashboards = 4
    expected_chips = 255


class M30SPlusPlusVE30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVE30
    expected_chips = 215


class M30SPlusPlusVE40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVE40
    expected_chips = 225


class M30SPlusPlusVE50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVE50
    expected_chips = 235


class M30SPlusPlusVF40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVF40
    expected_chips = 156


class M30SPlusPlusVG30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVG30
    expected_chips = 111


class M30SPlusPlusVG40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVG40
    expected_chips = 117


class M30SPlusPlusVG50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVG50


class M30SPlusPlusVH10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVH10
    expected_chips = 82


class M30SPlusPlusVH20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVH20
    expected_chips = 86


class M30SPlusPlusVH30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVH30
    expected_chips = 111


class M30SPlusPlusVH40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVH40
    expected_chips = 70


class M30SPlusPlusVH50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVH50
    expected_chips = 74


class M30SPlusPlusVH60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVH60
    expected_chips = 78


class M30SPlusPlusVH70(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVH70
    expected_chips = 70


class M30SPlusPlusVH80(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVH80
    expected_chips = 74


class M30SPlusPlusVH90(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVH90
    expected_chips = 78


class M30SPlusPlusVH100(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVH100
    expected_chips = 82


class M30SPlusPlusVJ20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVJ20


class M30SPlusPlusVJ30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SPlusPlusVJ30
