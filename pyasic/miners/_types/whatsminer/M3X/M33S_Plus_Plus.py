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

import warnings

from pyasic.miners._types.makes import WhatsMiner


class M33SPlusPlusVH20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M33S++ VH20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S++ VH20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 0


class M33SPlusPlusVH30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M33S++ VH30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S++ VH30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 0


class M33SPlusPlusVG40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M33S++ VG40"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S++ VG40, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 0
