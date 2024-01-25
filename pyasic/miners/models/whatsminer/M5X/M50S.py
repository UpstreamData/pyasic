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


class M50SVJ10(WhatsMinerMake):
    raw_model = "M50S VJ10"
    expected_fans = 2


class M50SVJ20(WhatsMinerMake):
    raw_model = "M50S VJ20"
    expected_fans = 2


class M50SVJ30(WhatsMinerMake):
    raw_model = "M50S VJ30"
    expected_fans = 2


class M50SVH10(WhatsMinerMake):
    raw_model = "M50S VH10"
    expected_fans = 2


class M50SVH20(WhatsMinerMake):
    raw_model = "M50S VH20"
    expected_chips = 135
    expected_fans = 2


class M50SVH30(WhatsMinerMake):
    raw_model = "M50S VH30"
    expected_chips = 156
    expected_fans = 2


class M50SVH40(WhatsMinerMake):
    raw_model = "M50S VH40"
    expected_fans = 2


class M50SVH50(WhatsMinerMake):
    raw_model = "M50S VH50"
    expected_fans = 2
