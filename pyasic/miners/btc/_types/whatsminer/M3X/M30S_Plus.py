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


class M30SPlusV10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ V10"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V10, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusV20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ V20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusV30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ V30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusV40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ V40"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V40, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusV50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ V50"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V50, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusV60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ V60"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V60, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusV70(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ V70"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V70, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusV80(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ V80"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V80, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusV90(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ V90"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V90, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusV100(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ V100"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V100, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVE30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VE30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVE40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VE40"
        self.nominal_chips = 156
        self.fan_count = 2


class M30SPlusVE50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VE50"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE50, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVE60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VE60"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE60, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVE70(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VE70"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE70, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVE80(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VE80"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE80, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVE90(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VE90"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE90, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVE100(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VE100"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE100, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVF20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VF20"
        self.nominal_chips = 111
        self.fan_count = 2


class M30SPlusVF30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VF30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VF30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M36SPlusVG30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M36S+ VG30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M36SPlusVG30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVG30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VG30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VG30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVG40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VG40"
        self.nominal_chips = 105
        self.fan_count = 2


class M30SPlusVG50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VG50"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VG50, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVG60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VG60"
        self.nominal_chips = 86
        self.fan_count = 2


class M30SPlusVH10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VH10"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VH10, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVH20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VH20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VH20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVH30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VH30"
        self.nominal_chips = 70
        self.fan_count = 2


class M30SPlusVH40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VH40"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VH40, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVH50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VH50"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VH50, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M30SPlusVH60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str, api_ver: str = "0.0.0"):
        super().__init__(ip, api_ver)
        self.ip = ip
        self.model = "M30S+ VH60"
        self.nominal_chips = 66
        self.fan_count = 2
