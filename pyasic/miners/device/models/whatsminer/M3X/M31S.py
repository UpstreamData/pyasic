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


class M31SV10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV10

    expected_chips = 105


class M31SV20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV20

    expected_chips = 111


class M31SV30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV30

    expected_chips = 117


class M31SV40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV40

    expected_chips = 123


class M31SV50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV50

    expected_chips = 78


class M31SV60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV60

    expected_chips = 105


class M31SV70(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV70

    expected_chips = 111


class M31SV80(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV80


class M31SV90(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV90

    expected_chips = 117


class M31SVE10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SVE10

    expected_chips = 70


class M31SVE20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SVE20

    expected_chips = 74


class M31SVE30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SVE30
