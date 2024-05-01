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

from pyasic.miners.backends import ePIC
from pyasic.miners.device.models import (
    S19,
    S19XP,
    S19j,
    S19jPro,
    S19jProPlus,
    S19kPro,
    S19Pro,
)


class ePICS19(ePIC, S19):
    pass


class ePICS19Pro(ePIC, S19Pro):
    pass


class ePICS19j(ePIC, S19j):
    pass


class ePICS19jPro(ePIC, S19jPro):
    pass


class ePICS19jProPlus(ePIC, S19jProPlus):
    pass


class ePICS19kPro(ePIC, S19kPro):
    pass


class ePICS19XP(ePIC, S19XP):
    pass
