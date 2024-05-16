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

from pyasic.device.makes import MinerMake
from pyasic.miners.base import BaseMiner


class WhatsMinerMake(BaseMiner):
    make = MinerMake.WHATSMINER


class AntMinerMake(BaseMiner):
    make = MinerMake.ANTMINER


class AvalonMinerMake(BaseMiner):
    make = MinerMake.AVALONMINER


class InnosiliconMake(BaseMiner):
    make = MinerMake.INNOSILICON


class GoldshellMake(BaseMiner):
    make = MinerMake.GOLDSHELL


class AuradineMake(BaseMiner):
    make = MinerMake.AURADINE


class ePICMake(BaseMiner):
    make = MinerMake.EPIC
