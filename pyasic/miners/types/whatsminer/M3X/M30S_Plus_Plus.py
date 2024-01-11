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

from pyasic.miners.makes import WhatsMiner


class M30SPlusPlusV10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ V10"
        self.expected_hashboards = 4
        self.expected_chips = 255
        self.fan_count = 2


class M30SPlusPlusV20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ V20"
        self.expected_hashboards = 4
        self.expected_chips = 255
        self.fan_count = 2


class M30SPlusPlusVE30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VE30"
        self.expected_chips = 215
        self.fan_count = 2


class M30SPlusPlusVE40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VE40"
        self.expected_chips = 225
        self.fan_count = 2


class M30SPlusPlusVE50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VE50"
        self.expected_chips = 235
        self.fan_count = 2


class M30SPlusPlusVF40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VF40"
        self.expected_chips = 156
        self.fan_count = 2


class M30SPlusPlusVG30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VG30"
        self.expected_chips = 111
        self.fan_count = 2


class M30SPlusPlusVG40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VG40"
        self.expected_chips = 117
        self.fan_count = 2


class M30SPlusPlusVG50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VG50"
        self.expected_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S++ VG50, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusPlusVH10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VH10"
        self.expected_chips = 82
        self.fan_count = 2


class M30SPlusPlusVH20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VH20"
        self.expected_chips = 86
        self.fan_count = 2


class M30SPlusPlusVH30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VH30"
        self.expected_chips = 111
        self.fan_count = 2


class M30SPlusPlusVH40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VH40"
        self.expected_chips = 70
        self.fan_count = 2


class M30SPlusPlusVH50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VH50"
        self.expected_chips = 74
        self.fan_count = 2


class M30SPlusPlusVH60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VH60"
        self.expected_chips = 78
        self.fan_count = 2


class M30SPlusPlusVH70(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VH70"
        self.expected_chips = 70
        self.fan_count = 2


class M30SPlusPlusVH80(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VH80"
        self.expected_chips = 74
        self.fan_count = 2


class M30SPlusPlusVH90(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VH90"
        self.expected_chips = 78
        self.fan_count = 2


class M30SPlusPlusVH100(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VH100"
        self.expected_chips = 82
        self.fan_count = 2


class M30SPlusPlusVJ20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VJ20"
        self.expected_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S++ VJ20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusPlusVJ30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.raw_model = "M30S++ VJ30"
        self.expected_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S++ VJ30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2
