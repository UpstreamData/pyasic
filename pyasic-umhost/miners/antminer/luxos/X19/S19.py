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

from pyasic.miners.backends import LUXMiner
from pyasic.miners.device.models import (
    S19,
    S19XP,
    S19jPro,
    S19jProPlus,
    S19kPro,
    S19Pro,
)


class LUXMinerS19(LUXMiner, S19):
    pass


class LUXMinerS19Pro(LUXMiner, S19Pro):
    pass


class LUXMinerS19jPro(LUXMiner, S19jPro):
    pass


class LUXMinerS19jProPlus(LUXMiner, S19jProPlus):
    pass


class LUXMinerS19kPro(LUXMiner, S19kPro):
    pass


class LUXMinerS19XP(LUXMiner, S19XP):
    pass
