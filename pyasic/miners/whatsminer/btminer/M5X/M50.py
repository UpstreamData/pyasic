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
from pyasic.miners.device.models import (
    M50VE30,
    M50VG30,
    M50VH10,
    M50VH20,
    M50VH30,
    M50VH40,
    M50VH50,
    M50VH60,
    M50VH70,
    M50VH80,
    M50VJ10,
    M50VJ20,
    M50VJ30,
)


class BTMinerM50VE30(M5X, M50VE30):
    pass


class BTMinerM50VG30(M5X, M50VG30):
    pass


class BTMinerM50VH10(M5X, M50VH10):
    pass


class BTMinerM50VH20(M5X, M50VH20):
    pass


class BTMinerM50VH30(M5X, M50VH30):
    pass


class BTMinerM50VH40(M5X, M50VH40):
    pass


class BTMinerM50VH50(M5X, M50VH50):
    pass


class BTMinerM50VH60(M5X, M50VH60):
    pass


class BTMinerM50VH70(M5X, M50VH70):
    pass


class BTMinerM50VH80(M5X, M50VH80):
    pass


class BTMinerM50VJ10(M5X, M50VJ10):
    pass


class BTMinerM50VJ20(M5X, M50VJ20):
    pass


class BTMinerM50VJ30(M5X, M50VJ30):
    pass
