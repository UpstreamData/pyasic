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


class M30SV10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SV10

    expected_chips = 148


class M30SV20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SV20

    expected_chips = 156


class M30SV30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SV30

    expected_chips = 164


class M30SV40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SV40

    expected_chips = 172


class M30SV50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SV50

    expected_chips = 156


class M30SV60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SV60

    expected_chips = 164


class M30SV70(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SV70


class M30SV80(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SV80

    expected_chips = 129


class M30SVE10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVE10

    expected_chips = 105


class M30SVE20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVE20

    expected_chips = 111


class M30SVE30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVE30

    expected_chips = 117


class M30SVE40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVE40

    expected_chips = 123


class M30SVE50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVE50

    expected_chips = 129


class M30SVE60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVE60


class M30SVE70(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVE70


class M30SVF10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVF10

    expected_chips = 70


class M30SVF20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVF20

    expected_chips = 74


class M30SVF30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVF30

    expected_chips = 78


class M30SVG10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVG10

    expected_chips = 66


class M30SVG20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVG20

    expected_chips = 70


class M30SVG30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVG30

    expected_chips = 74


class M30SVG40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVG40

    expected_chips = 78


class M30SVH10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVH10

    expected_chips = 64


class M30SVH20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVH20

    expected_chips = 66


class M30SVH30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVH30


class M30SVH40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVH40

    expected_chips = 64


class M30SVH50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVH50

    expected_chips = 66


class M30SVH60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVH60


class M30SVI20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30SVI20

    expected_chips = 70
