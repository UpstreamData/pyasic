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


class M31SPlusV10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusV10

    expected_chips = 105


class M31SPlusV20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusV20

    expected_chips = 111


class M31SPlusV30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusV30

    expected_chips = 117


class M31SPlusV40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusV40

    expected_chips = 123


class M31SPlusV50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusV50

    expected_chips = 148


class M31SPlusV60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusV60

    expected_chips = 156


class M31SPlusV80(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusV80

    expected_chips = 129


class M31SPlusV90(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusV90

    expected_chips = 117


class M31SPlusV100(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusV100

    expected_chips = 111


class M31SPlusVE10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusVE10

    expected_chips = 82


class M31SPlusVE20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusVE20

    expected_chips = 78


class M31SPlusVE30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusVE30

    expected_chips = 105


class M31SPlusVE40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusVE40

    expected_chips = 111


class M31SPlusVE50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusVE50

    expected_chips = 117


class M31SPlusVE60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusVE60


class M31SPlusVE80(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusVE80


class M31SPlusVF20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusVF20

    expected_chips = 66


class M31SPlusVF30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusVF30


class M31SPlusVG20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusVG20

    expected_chips = 66


class M31SPlusVG30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SPlusVG30

    expected_chips = 70
