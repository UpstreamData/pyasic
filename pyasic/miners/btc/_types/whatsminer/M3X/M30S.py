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


class M30SV10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S V10"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SV10, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SV20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S V20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SV20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SV30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S V30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SV30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SV40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S V40"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SV40, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SV50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S V50"
        self.nominal_chips = 156
        self.fan_count = 2


class M30SV60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S V60"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SV60, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SV70(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S V70"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SV70, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SV80(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S V80"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SV80, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVE10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VE10"
        self.nominal_chips = 105
        self.fan_count = 2


class M30SVE20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VE20"
        self.nominal_chips = 111
        self.fan_count = 2


class M30SVE30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VE30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVE30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVE40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VE40"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVE40, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVE50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VE50"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVE50, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVE60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VE60"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVE60, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVE70(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VE70"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVE70, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVF10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VF10"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVF10, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVF20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VF20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVF20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVF30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VF30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVF30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVG10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VG10"
        self.nominal_chips = 66
        self.fan_count = 2


class M30SVG20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VG20"
        self.nominal_chips = 70
        self.fan_count = 2


class M30SVG30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VG30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVG30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVG40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VG40"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVG40, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVH10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VH10"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVH10, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVH20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VH20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVH20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVH30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VH30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVH30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVH40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VH40"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVH40, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVH50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VH50"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVH50, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVH60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VH60"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVH60, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SVI20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S VI20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30SVI20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2
