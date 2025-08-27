# ------------------------------------------------------------------------------
#  Copyright 2025 Upstream Data Inc                                            -
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
from pyasic.device.algorithm.base import GenericAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import GoldshellMake


class Byte(GoldshellMake):
    raw_model = MinerModel.GOLDSHELL.Byte

    expected_chips = 0
    expected_fans = 0
    expected_hashboards = 0
    algo = GenericAlgo
