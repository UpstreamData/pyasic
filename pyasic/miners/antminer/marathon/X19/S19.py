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

from pyasic.miners.backends import MaraMiner
from pyasic.miners.device.models import (
    S19,
    S19XP,
    S19j,
    S19jNoPIC,
    S19jPro,
    S19KPro,
    S19Pro,
)


class MaraS19(MaraMiner, S19):
    pass


class MaraS19Pro(MaraMiner, S19Pro):
    pass


class MaraS19XP(MaraMiner, S19XP):
    pass


class MaraS19j(MaraMiner, S19j):
    pass


class MaraS19jNoPIC(MaraMiner, S19jNoPIC):
    pass


class MaraS19jPro(MaraMiner, S19jPro):
    pass


class MaraS19KPro(MaraMiner, S19KPro):
    pass
