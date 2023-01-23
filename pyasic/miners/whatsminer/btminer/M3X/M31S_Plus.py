#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from pyasic.miners._backends import BTMiner  # noqa - Ignore access to _module
from pyasic.miners._types import (  # noqa - Ignore access to _module
    M31SPlus,
    M31SPlusV30,
    M31SPlusV40,
    M31SPlusV60,
    M31SPlusV80,
    M31SPlusV90,
    M31SPlusVE20,
)


class BTMinerM31SPlus(BTMiner, M31SPlus):
    pass


class BTMinerM31SPlusVE20(BTMiner, M31SPlusVE20):
    pass


class BTMinerM31SPlusV30(BTMiner, M31SPlusV30):
    pass


class BTMinerM31SPlusV40(BTMiner, M31SPlusV40):
    pass


class BTMinerM31SPlusV60(BTMiner, M31SPlusV60):
    pass


class BTMinerM31SPlusV80(BTMiner, M31SPlusV80):
    pass


class BTMinerM31SPlusV90(BTMiner, M31SPlusV90):
    pass
