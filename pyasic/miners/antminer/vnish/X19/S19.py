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

from pyasic.miners.backends import VNish
from pyasic.miners.device.models import (
    S19,
    S19XP,
    S19a,
    S19aPro,
    S19j,
    S19jPro,
    S19NoPIC,
    S19Pro,
)


class VNishS19(VNish, S19):
    pass


class VNishS19NoPIC(VNish, S19NoPIC):
    pass


class VNishS19Pro(VNish, S19Pro):
    pass


class VNishS19XP(VNish, S19XP):
    pass


class VNishS19a(VNish, S19a):
    pass


class VNishS19aPro(VNish, S19aPro):
    pass


class VNishS19j(VNish, S19j):
    pass


class VNishS19jPro(VNish, S19jPro):
    pass
