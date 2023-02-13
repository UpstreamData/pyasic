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


class M50VG30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VG30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M50 VG30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M50VH10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VH10"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M50 VH10, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M50VH20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VH20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M50 VH20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M50VH30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VH30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M50 VH30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M50VH40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VH40"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M50 VH40, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M50VH50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VH50"
        self.nominal_chips = 105
        self.fan_count = 2


class M50VH60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VH60"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M50 VH60, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M50VH70(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VH70"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M50 VH70, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M50VH80(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VH80"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M50 VH80, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M50VJ10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VJ10"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M50 VJ10, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M50VJ20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VJ20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M50 VJ20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M50VJ30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M50 VJ30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M50 VJ30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2
