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

from pyasic.miners.backends import BOSer
from pyasic.miners.device.models import (
    S19,
    S19XP,
    S19a,
    S19aPro,
    S19j,
    S19jNoPIC,
    S19jPro,
    S19jProNoPIC,
    S19jProPlus,
    S19jProPlusNoPIC,
    S19kProNoPIC,
    S19Plus,
    S19Pro,
)


class BOSMinerS19(BOSer, S19):
    pass


class BOSMinerS19Plus(BOSer, S19Plus):
    pass


class BOSMinerS19Pro(BOSer, S19Pro):
    pass


class BOSMinerS19a(BOSer, S19a):
    pass


class BOSMinerS19j(BOSer, S19j):
    pass


class BOSMinerS19jNoPIC(BOSer, S19jNoPIC):
    pass


class BOSMinerS19jPro(BOSer, S19jPro):
    pass


class BOSMinerS19jProNoPIC(BOSer, S19jProNoPIC):
    pass


class BOSMinerS19kProNoPIC(BOSer, S19kProNoPIC):
    pass


class BOSMinerS19aPro(BOSer, S19aPro):
    pass


class BOSMinerS19jProPlus(BOSer, S19jProPlus):
    pass


class BOSMinerS19jProPlusNoPIC(BOSer, S19jProPlusNoPIC):
    pass


class BOSMinerS19XP(BOSer, S19XP):
    pass
