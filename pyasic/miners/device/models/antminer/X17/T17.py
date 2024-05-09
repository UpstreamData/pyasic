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


class T17(AntMinerMake):
    raw_model = MinerModel.ANTMINER.T17

    expected_chips = 30
    expected_fans = 4


class T17Plus(AntMinerMake):
    raw_model = MinerModel.ANTMINER.T17Plus

    expected_chips = 44
    expected_fans = 4


class T17e(AntMinerMake):
    raw_model = MinerModel.ANTMINER.T17e

    expected_chips = 78
    expected_fans = 4
