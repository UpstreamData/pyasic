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
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import AntMinerMake


class S19(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19

    expected_chips = 76
    expected_fans = 4


class S19NoPIC(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19NoPIC

    expected_chips = 88
    expected_fans = 4


class S19Pro(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19Pro

    expected_chips = 114
    expected_fans = 4


class S19i(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19i

    expected_chips = 80
    expected_fans = 4


class S19Plus(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19Plus

    expected_chips = 80
    expected_fans = 4


class S19ProPlus(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19ProPlus

    expected_chips = 120
    expected_fans = 4


class S19XP(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19XP

    expected_chips = 110
    expected_fans = 4


class S19a(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19a

    expected_chips = 72
    expected_fans = 4


class S19aPro(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19aPro

    expected_chips = 100
    expected_fans = 4


class S19j(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19j

    expected_chips = 114
    expected_fans = 4


class S19jNoPIC(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19jNoPIC

    expected_chips = 88
    expected_fans = 4


class S19jPro(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19jPro

    expected_chips = 126
    expected_fans = 4


class S19jProNoPIC(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19jProNoPIC

    expected_chips = 126
    expected_fans = 4


class S19jProPlus(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19jProPlus

    expected_chips = 120
    expected_fans = 4


class S19jProPlusNoPIC(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19jProPlusNoPIC

    expected_chips = 120
    expected_fans = 4


class S19kPro(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19kPro

    expected_chips = 77
    expected_fans = 4


class S19kProNoPIC(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19kProNoPIC

    expected_chips = 77
    expected_fans = 4


class S19L(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19L

    expected_chips = 76
    expected_fans = 4


class S19Hydro(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19Hydro

    expected_chips = 104
    expected_hashboards = 4
    expected_fans = 0


class S19ProHydro(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19ProHydro

    expected_chips = 180
    expected_hashboards = 4
    expected_fans = 0


class S19ProPlusHydro(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19ProPlusHydro

    expected_chips = 180
    expected_hashboards = 4
    expected_fans = 0


class S19KPro(AntMinerMake):
    raw_model = MinerModel.ANTMINER.S19KPro

    expected_chips = 77
    expected_fans = 4
