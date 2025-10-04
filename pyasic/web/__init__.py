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
from __future__ import annotations

from .antminer import AntminerModernWebAPI, AntminerOldWebAPI
from .auradine import AuradineWebAPI
from .avalonminer import AvalonMinerWebAPI
from .base import BaseWebAPI
from .braiins_os import BOSerWebAPI, BOSMinerWebAPI
from .elphapex import ElphapexWebAPI
from .epic import ePICWebAPI
from .espminer import ESPMinerWebAPI
from .goldshell import GoldshellWebAPI
from .hammer import HammerWebAPI
from .hiveon import HiveonWebAPI
from .iceriver import IceRiverWebAPI
from .innosilicon import InnosiliconWebAPI
from .marathon import MaraWebAPI
from .mskminer import MSKMinerWebAPI
from .vnish import VNishWebAPI

__all__ = [
    "BaseWebAPI",
    "AntminerModernWebAPI",
    "AntminerOldWebAPI",
    "AuradineWebAPI",
    "AvalonMinerWebAPI",
    "BOSerWebAPI",
    "BOSMinerWebAPI",
    "ElphapexWebAPI",
    "ePICWebAPI",
    "ESPMinerWebAPI",
    "GoldshellWebAPI",
    "HammerWebAPI",
    "HiveonWebAPI",
    "IceRiverWebAPI",
    "InnosiliconWebAPI",
    "MaraWebAPI",
    "MSKMinerWebAPI",
    "VNishWebAPI",
]
