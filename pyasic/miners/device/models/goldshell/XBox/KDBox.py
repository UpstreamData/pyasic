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
from pyasic.miners.device.makes import GoldshellMake


class KDBoxII(GoldshellMake):
    raw_model = MinerModel.GOLDSHELL.KDBoxII

    expected_chips = 36
    expected_hashboards = 1


class KDBoxPro(GoldshellMake):
    raw_model = MinerModel.GOLDSHELL.KDBoxPro

    expected_chips = 16
    expected_hashboards = 1
