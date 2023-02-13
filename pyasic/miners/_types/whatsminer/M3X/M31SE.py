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


class M31SEV10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31SE V10"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M31SEV10, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SEV20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31SE V20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M31SEV20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SEV30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31SE V30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M31SEV30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2
