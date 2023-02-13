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
    M50SPlusVH30,
    M50SPlusVH40,
    M50SPlusVJ30,
)


class BTMinerM50SPlusVH30(BTMiner, M50SPlusVH30):
    pass


class BTMinerM50SPlusVH40(BTMiner, M50SPlusVH40):
    pass


class BTMinerM50SPlusVJ30(BTMiner, M50SPlusVJ30):
    pass
