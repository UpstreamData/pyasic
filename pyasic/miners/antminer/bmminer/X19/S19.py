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

from pyasic.miners.backends import AntminerModern
from pyasic.miners.device.models import (
    S19,
    S19L,
    S19XP,
    S19a,
    S19aPro,
    S19Hydro,
    S19i,
    S19j,
    S19jNoPIC,
    S19jPro,
    S19KPro,
    S19Plus,
    S19Pro,
    S19ProHydro,
    S19ProPlus,
    S19ProPlusHydro,
)


class BMMinerS19(AntminerModern, S19):
    pass


class BMMinerS19Plus(AntminerModern, S19Plus):
    pass


class BMMinerS19i(AntminerModern, S19i):
    pass


class BMMinerS19Pro(AntminerModern, S19Pro):
    pass


class BMMinerS19ProPlus(AntminerModern, S19ProPlus):
    pass


class BMMinerS19XP(AntminerModern, S19XP):
    pass


class BMMinerS19a(AntminerModern, S19a):
    pass


class BMMinerS19aPro(AntminerModern, S19aPro):
    pass


class BMMinerS19j(AntminerModern, S19j):
    pass


class BMMinerS19jNoPIC(AntminerModern, S19jNoPIC):
    pass


class BMMinerS19jPro(AntminerModern, S19jPro):
    pass


class BMMinerS19L(AntminerModern, S19L):
    pass


class BMMinerS19ProHydro(AntminerModern, S19ProHydro):
    pass


class BMMinerS19Hydro(AntminerModern, S19Hydro):
    pass


class BMMinerS19ProPlusHydro(AntminerModern, S19ProPlusHydro):
    pass


class BMMinerS19KPro(AntminerModern, S19KPro):
    pass
