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

from pyasic.miners._backends import BTMiner  # noqa - Ignore access to _module
from pyasic.miners._types import (  # noqa - Ignore access to _module
    M31SV10,
    M31SV20,
    M31SV30,
    M31SV40,
    M31SV50,
    M31SV60,
    M31SV70,
    M31SV80,
    M31SV90,
    M31SVE10,
    M31SVE20,
    M31SVE30,
)


class BTMinerM31SV10(BTMiner, M31SV10):
    pass


class BTMinerM31SV20(BTMiner, M31SV20):
    pass


class BTMinerM31SV30(BTMiner, M31SV30):
    pass


class BTMinerM31SV40(BTMiner, M31SV40):
    pass


class BTMinerM31SV50(BTMiner, M31SV50):
    pass


class BTMinerM31SV60(BTMiner, M31SV60):
    pass


class BTMinerM31SV70(BTMiner, M31SV70):
    pass


class BTMinerM31SV80(BTMiner, M31SV80):
    pass


class BTMinerM31SV90(BTMiner, M31SV90):
    pass


class BTMinerM31SVE10(BTMiner, M31SVE10):
    pass


class BTMinerM31SVE20(BTMiner, M31SVE20):
    pass


class BTMinerM31SVE30(BTMiner, M31SVE30):
    pass
