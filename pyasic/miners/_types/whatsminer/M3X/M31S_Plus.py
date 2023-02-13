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


class M31SPlusV10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V10"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V10, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusV20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusV30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V30"
        self.nominal_chips = 117
        self.fan_count = 2


class M31SPlusV40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V40"
        self.nominal_chips = 123
        self.fan_count = 2


class M31SPlusV50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V50"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ V50, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusV60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V60"
        self.nominal_chips = 156
        self.fan_count = 2


class M31SPlusV80(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V80"
        self.nominal_chips = 129
        self.fan_count = 2


class M31SPlusV90(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V90"
        self.nominal_chips = 117
        self.fan_count = 2


class M31SPlusV100(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V100"
        self.nominal_chips = 111
        self.fan_count = 2


class M31SPlusVE10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VE10"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE10, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusVE20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VE20"
        self.nominal_chips = 78
        self.fan_count = 2


class M31SPlusVE30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VE30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusVE40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VE40"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE40, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusVE50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VE50"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE50, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusVE60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VE60"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE60, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusVE80(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VE80"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VE80, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusVF20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VF20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VF20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusVF30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VF30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VF30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusVG20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VG20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VG20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusVG30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ VG30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M30S+ VG30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SPlusV30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V30"
        self.nominal_chips = 117
        self.fan_count = 2


class M31SPlusV40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+ V40"
        self.nominal_chips = 123
        self.fan_count = 2
