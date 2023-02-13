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
    M50SVH10,
    M50SVH20,
    M50SVH30,
    M50SVH40,
    M50SVH50,
    M50SVJ10,
    M50SVJ20,
    M50SVJ30,
)


class BTMinerM50SVJ10(BTMiner, M50SVJ10):
    pass


class BTMinerM50SVJ20(BTMiner, M50SVJ20):
    pass


class BTMinerM50SVJ30(BTMiner, M50SVJ30):
    pass


class BTMinerM50SVH10(BTMiner, M50SVH10):
    pass


class BTMinerM50SVH20(BTMiner, M50SVH20):
    pass


class BTMinerM50SVH30(BTMiner, M50SVH30):
    pass


class BTMinerM50SVH40(BTMiner, M50SVH40):
    pass


class BTMinerM50SVH50(BTMiner, M50SVH50):
    pass
