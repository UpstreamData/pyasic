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

from pyasic.miners.makes import WhatsMinerMake


class M30SPlusPlusV10(WhatsMinerMake):
    raw_model = "M30S++ V10"
    expected_hashboards = 4
    expected_chips = 255
    expected_fans = 2


class M30SPlusPlusV20(WhatsMinerMake):
    raw_model = "M30S++ V20"
    expected_hashboards = 4
    expected_chips = 255
    expected_fans = 2


class M30SPlusPlusVE30(WhatsMinerMake):
    raw_model = "M30S++ VE30"
    expected_chips = 215
    expected_fans = 2


class M30SPlusPlusVE40(WhatsMinerMake):
    raw_model = "M30S++ VE40"
    expected_chips = 225
    expected_fans = 2


class M30SPlusPlusVE50(WhatsMinerMake):
    raw_model = "M30S++ VE50"
    expected_chips = 235
    expected_fans = 2


class M30SPlusPlusVF40(WhatsMinerMake):
    raw_model = "M30S++ VF40"
    expected_chips = 156
    expected_fans = 2


class M30SPlusPlusVG30(WhatsMinerMake):
    raw_model = "M30S++ VG30"
    expected_chips = 111
    expected_fans = 2


class M30SPlusPlusVG40(WhatsMinerMake):
    raw_model = "M30S++ VG40"
    expected_chips = 117
    expected_fans = 2


class M30SPlusPlusVG50(WhatsMinerMake):
    raw_model = "M30S++ VG50"
    expected_fans = 2


class M30SPlusPlusVH10(WhatsMinerMake):
    raw_model = "M30S++ VH10"
    expected_chips = 82
    expected_fans = 2


class M30SPlusPlusVH20(WhatsMinerMake):
    raw_model = "M30S++ VH20"
    expected_chips = 86
    expected_fans = 2


class M30SPlusPlusVH30(WhatsMinerMake):
    raw_model = "M30S++ VH30"
    expected_chips = 111
    expected_fans = 2


class M30SPlusPlusVH40(WhatsMinerMake):
    raw_model = "M30S++ VH40"
    expected_chips = 70
    expected_fans = 2


class M30SPlusPlusVH50(WhatsMinerMake):
    raw_model = "M30S++ VH50"
    expected_chips = 74
    expected_fans = 2


class M30SPlusPlusVH60(WhatsMinerMake):
    raw_model = "M30S++ VH60"
    expected_chips = 78
    expected_fans = 2


class M30SPlusPlusVH70(WhatsMinerMake):
    raw_model = "M30S++ VH70"
    expected_chips = 70
    expected_fans = 2


class M30SPlusPlusVH80(WhatsMinerMake):
    raw_model = "M30S++ VH80"
    expected_chips = 74
    expected_fans = 2


class M30SPlusPlusVH90(WhatsMinerMake):
    raw_model = "M30S++ VH90"
    expected_chips = 78
    expected_fans = 2


class M30SPlusPlusVH100(WhatsMinerMake):
    raw_model = "M30S++ VH100"
    expected_chips = 82
    expected_fans = 2


class M30SPlusPlusVJ20(WhatsMinerMake):
    raw_model = "M30S++ VJ20"
    expected_fans = 2


class M30SPlusPlusVJ30(WhatsMinerMake):
    raw_model = "M30S++ VJ30"
    expected_fans = 2
