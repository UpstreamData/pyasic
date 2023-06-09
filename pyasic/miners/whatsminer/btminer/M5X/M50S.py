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

from pyasic.miners.backends import M5X
from pyasic.miners.types import (
    M50SVH10,
    M50SVH20,
    M50SVH30,
    M50SVH40,
    M50SVH50,
    M50SVJ10,
    M50SVJ20,
    M50SVJ30,
)


class BTMinerM50SVJ10(M5X, M50SVJ10):
    pass


class BTMinerM50SVJ20(M5X, M50SVJ20):
    pass


class BTMinerM50SVJ30(M5X, M50SVJ30):
    pass


class BTMinerM50SVH10(M5X, M50SVH10):
    pass


class BTMinerM50SVH20(M5X, M50SVH20):
    pass


class BTMinerM50SVH30(M5X, M50SVH30):
    pass


class BTMinerM50SVH40(M5X, M50SVH40):
    pass


class BTMinerM50SVH50(M5X, M50SVH50):
    pass
