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


class M31SV10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S V10"
        self.nominal_chips = 105
        self.fan_count = 2


class M31SV20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S V20"
        self.nominal_chips = 111
        self.fan_count = 2


class M31SV30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S V30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M31SV30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SV40(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S V40"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M31SV40, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SV50(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S V50"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M31SV50, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SV60(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S V60"
        self.nominal_chips = 105
        self.fan_count = 2


class M31SV70(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S V70"
        self.nominal_chips = 111
        self.fan_count = 2


class M31SV80(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S V80"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M31SV80, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SV90(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S V90"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M31SV90, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SVE10(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S VE10"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M31SVE10, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SVE20(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S VE20"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M31SVE20, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2


class M31SVE30(WhatsMiner):  # noqa - ignore ABC method implementation
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S VE30"
        self.nominal_chips = 0
        warnings.warn(
            "Unknown chip count for miner type M31SVE30, please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
        )
        self.fan_count = 2
