# ------------------------------------------------------------------------------
#  Copyright 2023 Upstream Data Inc                                            -
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

from pyasic.miners.backends import M6X
from pyasic.miners.device.models import M60VK10, M60VK20, M60VK30, M60VK40


class BTMinerM60VK10(M6X, M60VK10):
    pass


class BTMinerM60VK20(M6X, M60VK20):
    pass


class BTMinerM60VK30(M6X, M60VK30):
    pass


class BTMinerM60VK40(M6X, M60VK40):
    pass
