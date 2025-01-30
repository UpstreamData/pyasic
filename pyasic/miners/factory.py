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

import asyncio
import enum
import ipaddress
import json
import re
import warnings
from typing import Any, AsyncGenerator, Callable

import anyio
import httpx

from pyasic import settings
from pyasic.logger import logger
from pyasic.miners.antminer import *
from pyasic.miners.auradine import *
from pyasic.miners.avalonminer import *
from pyasic.miners.backends import *
from pyasic.miners.base import AnyMiner
from pyasic.miners.bitaxe import *
from pyasic.miners.blockminer import *
from pyasic.miners.braiins import *
from pyasic.miners.device.makes import *
from pyasic.miners.goldshell import *
from pyasic.miners.hammer import *
from pyasic.miners.iceriver import *
from pyasic.miners.innosilicon import *
from pyasic.miners.luckyminer import *
from pyasic.miners.volcminer import *
from pyasic.miners.whatsminer import *


class MinerTypes(enum.Enum):
    ANTMINER = 0
    WHATSMINER = 1
    AVALONMINER = 2
    INNOSILICON = 3
    GOLDSHELL = 4
    BRAIINS_OS = 5
    VNISH = 6
    HIVEON = 7
    LUX_OS = 8
    EPIC = 9
    AURADINE = 10
    MARATHON = 11
    BITAXE = 12
    ICERIVER = 13
    HAMMER = 14
    VOLCMINER = 15
    LUCKYMINER = 16


MINER_CLASSES = {
    MinerTypes.ANTMINER: {
        None: type("AntminerUnknown", (BMMiner, AntMinerMake), {}),
        "ANTMINER D3": CGMinerD3,
        "ANTMINER HS3": BMMinerHS3,
        "ANTMINER L3+": BMMinerL3Plus,
        "ANTMINER KA3": BMMinerKA3,
        "ANTMINER KS3": BMMinerKS3,
        "ANTMINER DR5": CGMinerDR5,
        "ANTMINER KS5": BMMinerKS5,
        "ANTMINER KS5 PRO": BMMinerKS5Pro,
        "ANTMINER L7": BMMinerL7,
        "ANTMINER K7": BMMinerK7,
        "ANTMINER D7": BMMinerD7,
        "ANTMINER E9 PRO": BMMinerE9Pro,
        "ANTMINER D9": BMMinerD9,
        "ANTMINER S9": BMMinerS9,
        "ANTMINER S9I": BMMinerS9i,
        "ANTMINER S9J": BMMinerS9j,
        "ANTMINER T9": BMMinerT9,
        "ANTMINER L9": BMMinerL9,
        "ANTMINER Z15": CGMinerZ15,
        "ANTMINER Z15 PRO": BMMinerZ15Pro,
        "ANTMINER S17": BMMinerS17,
        "ANTMINER S17+": BMMinerS17Plus,
        "ANTMINER S17 PRO": BMMinerS17Pro,
        "ANTMINER S17E": BMMinerS17e,
        "ANTMINER T17": BMMinerT17,
        "ANTMINER T17+": BMMinerT17Plus,
        "ANTMINER T17E": BMMinerT17e,
        "ANTMINER S19": BMMinerS19,
        "ANTMINER S19L": BMMinerS19L,
        "ANTMINER S19 PRO": BMMinerS19Pro,
        "ANTMINER S19J": BMMinerS19j,
        "ANTMINER S19I": BMMinerS19i,
        "ANTMINER S19+": BMMinerS19Plus,
        "ANTMINER S19J88NOPIC": BMMinerS19jNoPIC,
        "ANTMINER S19PRO+": BMMinerS19ProPlus,
        "ANTMINER S19J PRO": BMMinerS19jPro,
        "ANTMINER S19 XP": BMMinerS19XP,
        "ANTMINER S19A": BMMinerS19a,
        "ANTMINER S19A PRO": BMMinerS19aPro,
        "ANTMINER S19 HYDRO": BMMinerS19Hydro,
        "ANTMINER S19 PRO HYD.": BMMinerS19ProHydro,
        "ANTMINER S19 PRO+ HYD.": BMMinerS19ProPlusHydro,
        "ANTMINER S19K PRO": BMMinerS19KPro,
        "ANTMINER S19J XP": BMMinerS19jXP,
        "ANTMINER T19": BMMinerT19,
        "ANTMINER S21": BMMinerS21,
        "ANTMINER BHB68601": BMMinerS21,  # ???
        "ANTMINER BHB68606": BMMinerS21,  # ???
        "ANTMINER S21 PRO": BMMinerS21Pro,
        "ANTMINER T21": BMMinerT21,
        "ANTMINER S21 HYD.": BMMinerS21Hydro,
    },
    MinerTypes.WHATSMINER: {
        None: type("WhatsminerUnknown", (BTMiner, WhatsMinerMake), {}),
        "M20PV10": BTMinerM20PV10,
        "M20PV30": BTMinerM20PV30,
        "M20S+V30": BTMinerM20SPlusV30,
        "M20SV10": BTMinerM20SV10,
        "M20SV20": BTMinerM20SV20,
        "M20SV30": BTMinerM20SV30,
        "M20V10": BTMinerM20V10,
        "M21S+V20": BTMinerM21SPlusV20,
        "M21SV20": BTMinerM21SV20,
        "M21SV60": BTMinerM21SV60,
        "M21SV70": BTMinerM21SV70,
        "M21V10": BTMinerM21V10,
        "M29V10": BTMinerM29V10,
        "M30KV10": BTMinerM30KV10,
        "M30LV10": BTMinerM30LV10,
        "M30S++V10": BTMinerM30SPlusPlusV10,
        "M30S++V20": BTMinerM30SPlusPlusV20,
        "M30S++VE30": BTMinerM30SPlusPlusVE30,
        "M30S++VE40": BTMinerM30SPlusPlusVE40,
        "M30S++VE50": BTMinerM30SPlusPlusVE50,
        "M30S++VF40": BTMinerM30SPlusPlusVF40,
        "M30S++VG30": BTMinerM30SPlusPlusVG30,
        "M30S++VG40": BTMinerM30SPlusPlusVG40,
        "M30S++VG50": BTMinerM30SPlusPlusVG50,
        "M30S++VH10": BTMinerM30SPlusPlusVH10,
        "M30S++VH100": BTMinerM30SPlusPlusVH100,
        "M30S++VH110": BTMinerM30SPlusPlusVH110,
        "M30S++VH20": BTMinerM30SPlusPlusVH20,
        "M30S++VH30": BTMinerM30SPlusPlusVH30,
        "M30S++VH40": BTMinerM30SPlusPlusVH40,
        "M30S++VH50": BTMinerM30SPlusPlusVH50,
        "M30S++VH60": BTMinerM30SPlusPlusVH60,
        "M30S++VH70": BTMinerM30SPlusPlusVH70,
        "M30S++VH80": BTMinerM30SPlusPlusVH80,
        "M30S++VH90": BTMinerM30SPlusPlusVH90,
        "M30S++VI30": BTMinerM30SPlusPlusVI30,
        "M30S++VJ20": BTMinerM30SPlusPlusVJ20,
        "M30S++VJ30": BTMinerM30SPlusPlusVJ30,
        "M30S++VJ50": BTMinerM30SPlusPlusVJ50,
        "M30S++VJ60": BTMinerM30SPlusPlusVJ60,
        "M30S++VJ70": BTMinerM30SPlusPlusVJ70,
        "M30S++VK30": BTMinerM30SPlusPlusVK30,
        "M30S++VK40": BTMinerM30SPlusPlusVK40,
        "M30S+V10": BTMinerM30SPlusV10,
        "M30S+V100": BTMinerM30SPlusV100,
        "M30S+V20": BTMinerM30SPlusV20,
        "M30S+V30": BTMinerM30SPlusV30,
        "M30S+V40": BTMinerM30SPlusV40,
        "M30S+V50": BTMinerM30SPlusV50,
        "M30S+V60": BTMinerM30SPlusV60,
        "M30S+V70": BTMinerM30SPlusV70,
        "M30S+V80": BTMinerM30SPlusV80,
        "M30S+V90": BTMinerM30SPlusV90,
        "M30S+VE100": BTMinerM30SPlusVE100,
        "M30S+VE30": BTMinerM30SPlusVE30,
        "M30S+VE40": BTMinerM30SPlusVE40,
        "M30S+VE50": BTMinerM30SPlusVE50,
        "M30S+VE60": BTMinerM30SPlusVE60,
        "M30S+VE70": BTMinerM30SPlusVE70,
        "M30S+VE80": BTMinerM30SPlusVE80,
        "M30S+VE90": BTMinerM30SPlusVE90,
        "M30S+VF20": BTMinerM30SPlusVF20,
        "M30S+VF30": BTMinerM30SPlusVF30,
        "M30S+VG20": BTMinerM30SPlusVG20,
        "M30S+VG30": BTMinerM30SPlusVG30,
        "M30S+VG40": BTMinerM30SPlusVG40,
        "M30S+VG50": BTMinerM30SPlusVG50,
        "M30S+VG60": BTMinerM30SPlusVG60,
        "M30S+VH10": BTMinerM30SPlusVH10,
        "M30S+VH20": BTMinerM30SPlusVH20,
        "M30S+VH30": BTMinerM30SPlusVH30,
        "M30S+VH40": BTMinerM30SPlusVH40,
        "M30S+VH50": BTMinerM30SPlusVH50,
        "M30S+VH60": BTMinerM30SPlusVH60,
        "M30S+VH70": BTMinerM30SPlusVH70,
        "M30S+VI30": BTMinerM30SPlusVI30,
        "M30S+VJ30": BTMinerM30SPlusVJ30,
        "M30S+VJ40": BTMinerM30SPlusVJ40,
        "M30SV10": BTMinerM30SV10,
        "M30SV20": BTMinerM30SV20,
        "M30SV30": BTMinerM30SV30,
        "M30SV40": BTMinerM30SV40,
        "M30SV50": BTMinerM30SV50,
        "M30SV60": BTMinerM30SV60,
        "M30SV70": BTMinerM30SV70,
        "M30SV80": BTMinerM30SV80,
        "M30SVE10": BTMinerM30SVE10,
        "M30SVE20": BTMinerM30SVE20,
        "M30SVE30": BTMinerM30SVE30,
        "M30SVE40": BTMinerM30SVE40,
        "M30SVE50": BTMinerM30SVE50,
        "M30SVE60": BTMinerM30SVE60,
        "M30SVE70": BTMinerM30SVE70,
        "M30SVF10": BTMinerM30SVF10,
        "M30SVF20": BTMinerM30SVF20,
        "M30SVF30": BTMinerM30SVF30,
        "M30SVG10": BTMinerM30SVG10,
        "M30SVG20": BTMinerM30SVG20,
        "M30SVG30": BTMinerM30SVG30,
        "M30SVG40": BTMinerM30SVG40,
        "M30SVH10": BTMinerM30SVH10,
        "M30SVH20": BTMinerM30SVH20,
        "M30SVH30": BTMinerM30SVH30,
        "M30SVH40": BTMinerM30SVH40,
        "M30SVH50": BTMinerM30SVH50,
        "M30SVH60": BTMinerM30SVH60,
        "M30SVI20": BTMinerM30SVI20,
        "M30SVJ30": BTMinerM30SVJ30,
        "M30V10": BTMinerM30V10,
        "M30V20": BTMinerM30V20,
        "M31HV10": BTMinerM31HV10,
        "M31HV40": BTMinerM31HV40,
        "M31LV10": BTMinerM31LV10,
        "M31S+V10": BTMinerM31SPlusV10,
        "M31S+V100": BTMinerM31SPlusV100,
        "M31S+V20": BTMinerM31SPlusV20,
        "M31S+V30": BTMinerM31SPlusV30,
        "M31S+V40": BTMinerM31SPlusV40,
        "M31S+V50": BTMinerM31SPlusV50,
        "M31S+V60": BTMinerM31SPlusV60,
        "M31S+V80": BTMinerM31SPlusV80,
        "M31S+V90": BTMinerM31SPlusV90,
        "M31S+VE10": BTMinerM31SPlusVE10,
        "M31S+VE20": BTMinerM31SPlusVE20,
        "M31S+VE30": BTMinerM31SPlusVE30,
        "M31S+VE40": BTMinerM31SPlusVE40,
        "M31S+VE50": BTMinerM31SPlusVE50,
        "M31S+VE60": BTMinerM31SPlusVE60,
        "M31S+VE80": BTMinerM31SPlusVE80,
        "M31S+VF20": BTMinerM31SPlusVF20,
        "M31S+VF30": BTMinerM31SPlusVF30,
        "M31S+VG20": BTMinerM31SPlusVG20,
        "M31S+VG30": BTMinerM31SPlusVG30,
        "M31SEV10": BTMinerM31SEV10,
        "M31SEV20": BTMinerM31SEV20,
        "M31SEV30": BTMinerM31SEV30,
        "M31SV10": BTMinerM31SV10,
        "M31SV20": BTMinerM31SV20,
        "M31SV30": BTMinerM31SV30,
        "M31SV40": BTMinerM31SV40,
        "M31SV50": BTMinerM31SV50,
        "M31SV60": BTMinerM31SV60,
        "M31SV70": BTMinerM31SV70,
        "M31SV80": BTMinerM31SV80,
        "M31SV90": BTMinerM31SV90,
        "M31SVE10": BTMinerM31SVE10,
        "M31SVE20": BTMinerM31SVE20,
        "M31SVE30": BTMinerM31SVE30,
        "M31V10": BTMinerM31V10,
        "M31V20": BTMinerM31V20,
        "M32V10": BTMinerM32V10,
        "M32V20": BTMinerM32V20,
        "M33S++VG40": BTMinerM33SPlusPlusVG40,
        "M33S++VH20": BTMinerM33SPlusPlusVH20,
        "M33S++VH30": BTMinerM33SPlusPlusVH30,
        "M33S+VG20": BTMinerM33SPlusVG20,
        "M33S+VG30": BTMinerM33SPlusVG30,
        "M33S+VH20": BTMinerM33SPlusVH20,
        "M33S+VH30": BTMinerM33SPlusVH30,
        "M33SVG30": BTMinerM33SVG30,
        "M33V10": BTMinerM33V10,
        "M33V20": BTMinerM33V20,
        "M33V30": BTMinerM33V30,
        "M34S+VE10": BTMinerM34SPlusVE10,
        "M36S++VH30": BTMinerM36SPlusPlusVH30,
        "M36S+VG30": BTMinerM36SPlusVG30,
        "M36SVE10": BTMinerM36SVE10,
        "M39V10": BTMinerM39V10,
        "M39V20": BTMinerM39V20,
        "M39V30": BTMinerM39V30,
        "M50S++VK10": BTMinerM50SPlusPlusVK10,
        "M50S++VK20": BTMinerM50SPlusPlusVK20,
        "M50S++VK30": BTMinerM50SPlusPlusVK30,
        "M50S++VK40": BTMinerM50SPlusPlusVK40,
        "M50S++VK50": BTMinerM50SPlusPlusVK50,
        "M50S++VK60": BTMinerM50SPlusPlusVK60,
        "M50S++VL20": BTMinerM50SPlusPlusVL20,
        "M50S++VL30": BTMinerM50SPlusPlusVL30,
        "M50S++VL40": BTMinerM50SPlusPlusVL40,
        "M50S++VL50": BTMinerM50SPlusPlusVL50,
        "M50S++VL60": BTMinerM50SPlusPlusVL60,
        "M50S+VH30": BTMinerM50SPlusVH30,
        "M50S+VH40": BTMinerM50SPlusVH40,
        "M50S+VJ30": BTMinerM50SPlusVJ30,
        "M50S+VJ40": BTMinerM50SPlusVJ40,
        "M50S+VJ60": BTMinerM50SPlusVJ60,
        "M50S+VK10": BTMinerM50SPlusVK10,
        "M50S+VK20": BTMinerM50SPlusVK20,
        "M50S+VK30": BTMinerM50SPlusVK30,
        "M50S+VL10": BTMinerM50SPlusVL10,
        "M50S+VL20": BTMinerM50SPlusVL20,
        "M50S+VL30": BTMinerM50SPlusVL30,
        "M50SVH10": BTMinerM50SVH10,
        "M50SVH20": BTMinerM50SVH20,
        "M50SVH30": BTMinerM50SVH30,
        "M50SVH40": BTMinerM50SVH40,
        "M50SVH50": BTMinerM50SVH50,
        "M50SVJ10": BTMinerM50SVJ10,
        "M50SVJ20": BTMinerM50SVJ20,
        "M50SVJ30": BTMinerM50SVJ30,
        "M50SVJ40": BTMinerM50SVJ40,
        "M50SVJ50": BTMinerM50SVJ50,
        "M50SVK10": BTMinerM50SVK10,
        "M50SVK20": BTMinerM50SVK20,
        "M50SVK30": BTMinerM50SVK30,
        "M50SVK50": BTMinerM50SVK50,
        "M50SVK60": BTMinerM50SVK60,
        "M50SVK70": BTMinerM50SVK70,
        "M50SVK80": BTMinerM50SVK80,
        "M50SVL20": BTMinerM50SVL20,
        "M50SVL30": BTMinerM50SVL30,
        "M50VE30": BTMinerM50VE30,
        "M50VG30": BTMinerM50VG30,
        "M50VH10": BTMinerM50VH10,
        "M50VH20": BTMinerM50VH20,
        "M50VH30": BTMinerM50VH30,
        "M50VH40": BTMinerM50VH40,
        "M50VH50": BTMinerM50VH50,
        "M50VH60": BTMinerM50VH60,
        "M50VH70": BTMinerM50VH70,
        "M50VH80": BTMinerM50VH80,
        "M50VH90": BTMinerM50VH90,
        "M50VJ10": BTMinerM50VJ10,
        "M50VJ20": BTMinerM50VJ20,
        "M50VJ30": BTMinerM50VJ30,
        "M50VJ40": BTMinerM50VJ40,
        "M50VJ60": BTMinerM50VJ60,
        "M50VK40": BTMinerM50VK40,
        "M50VK50": BTMinerM50VK50,
        "M52S++VL10": BTMinerM52SPlusPlusVL10,
        "M52SVK30": BTMinerM52SVK30,
        "M53HVH10": BTMinerM53HVH10,
        "M53S++VK10": BTMinerM53SPlusPlusVK10,
        "M53S++VK20": BTMinerM53SPlusPlusVK20,
        "M53S++VK30": BTMinerM53SPlusPlusVK30,
        "M53S++VK50": BTMinerM53SPlusPlusVK50,
        "M53S++VL10": BTMinerM53SPlusPlusVL10,
        "M53S++VL30": BTMinerM53SPlusPlusVL30,
        "M53S+VJ30": BTMinerM53SPlusVJ30,
        "M53S+VJ40": BTMinerM53SPlusVJ40,
        "M53S+VJ50": BTMinerM53SPlusVJ50,
        "M53S+VK30": BTMinerM53SPlusVK30,
        "M53SVH20": BTMinerM53SVH20,
        "M53SVH30": BTMinerM53SVH30,
        "M53SVJ30": BTMinerM53SVJ30,
        "M53SVJ40": BTMinerM53SVJ40,
        "M53SVK30": BTMinerM53SVK30,
        "M53VH30": BTMinerM53VH30,
        "M53VH40": BTMinerM53VH40,
        "M53VH50": BTMinerM53VH50,
        "M53VK30": BTMinerM53VK30,
        "M53VK60": BTMinerM53VK60,
        "M54S++VK30": BTMinerM54SPlusPlusVK30,
        "M54S++VL30": BTMinerM54SPlusPlusVL30,
        "M54S++VL40": BTMinerM54SPlusPlusVL40,
        "M56S++VK10": BTMinerM56SPlusPlusVK10,
        "M56S++VK30": BTMinerM56SPlusPlusVK30,
        "M56S++VK40": BTMinerM56SPlusPlusVK40,
        "M56S++VK50": BTMinerM56SPlusPlusVK50,
        "M56S+VJ30": BTMinerM56SPlusVJ30,
        "M56S+VK30": BTMinerM56SPlusVK30,
        "M56S+VK40": BTMinerM56SPlusVK40,
        "M56S+VK50": BTMinerM56SPlusVK50,
        "M56SVH30": BTMinerM56SVH30,
        "M56SVJ30": BTMinerM56SVJ30,
        "M56SVJ40": BTMinerM56SVJ40,
        "M56VH30": BTMinerM56VH30,
        "M59VH30": BTMinerM59VH30,
        "M60S++VL30": BTMinerM60SPlusPlusVL30,
        "M60S++VL40": BTMinerM60SPlusPlusVL40,
        "M60S+VK30": BTMinerM60SPlusVK30,
        "M60S+VK40": BTMinerM60SPlusVK40,
        "M60S+VK50": BTMinerM60SPlusVK50,
        "M60S+VK60": BTMinerM60SPlusVK60,
        "M60S+VK70": BTMinerM60SPlusVK70,
        "M60S+VL10": BTMinerM60SPlusVL10,
        "M60S+VL30": BTMinerM60SPlusVL30,
        "M60S+VL40": BTMinerM60SPlusVL40,
        "M60S+VL50": BTMinerM60SPlusVL50,
        "M60S+VL60": BTMinerM60SPlusVL60,
        "M60SVK10": BTMinerM60SVK10,
        "M60SVK20": BTMinerM60SVK20,
        "M60SVK30": BTMinerM60SVK30,
        "M60SVK40": BTMinerM60SVK40,
        "M60SVL10": BTMinerM60SVL10,
        "M60SVL20": BTMinerM60SVL20,
        "M60SVL30": BTMinerM60SVL30,
        "M60SVL40": BTMinerM60SVL40,
        "M60SVL50": BTMinerM60SVL50,
        "M60SVL60": BTMinerM60SVL60,
        "M60SVL70": BTMinerM60SVL70,
        "M60VK10": BTMinerM60VK10,
        "M60VK20": BTMinerM60VK20,
        "M60VK30": BTMinerM60VK30,
        "M60VK40": BTMinerM60VK40,
        "M60VK6A": BTMinerM60VK6A,
        "M60VL10": BTMinerM60VL10,
        "M60VL20": BTMinerM60VL20,
        "M60VL30": BTMinerM60VL30,
        "M60VL40": BTMinerM60VL40,
        "M60VL50": BTMinerM60VL50,
        "M61S+VL30": BTMinerM61SPlusVL30,
        "M61SVL10": BTMinerM61SVL10,
        "M61SVL20": BTMinerM61SVL20,
        "M61SVL30": BTMinerM61SVL30,
        "M61VK10": BTMinerM61VK10,
        "M61VK20": BTMinerM61VK20,
        "M61VK30": BTMinerM61VK30,
        "M61VK40": BTMinerM61VK40,
        "M61VL10": BTMinerM61VL10,
        "M61VL30": BTMinerM61VL30,
        "M61VL40": BTMinerM61VL40,
        "M61VL50": BTMinerM61VL50,
        "M61VL60": BTMinerM61VL60,
        "M62S+VK30": BTMinerM62SPlusVK30,
        "M63S++VL20": BTMinerM63SPlusPlusVL20,
        "M63S+VK30": BTMinerM63SPlusVK30,
        "M63S+VL10": BTMinerM63SPlusVL10,
        "M63S+VL20": BTMinerM63SPlusVL20,
        "M63S+VL30": BTMinerM63SPlusVL30,
        "M63S+VL50": BTMinerM63SPlusVL50,
        "M63SVK10": BTMinerM63SVK10,
        "M63SVK20": BTMinerM63SVK20,
        "M63SVK30": BTMinerM63SVK30,
        "M63SVK60": BTMinerM63SVK60,
        "M63SVL10": BTMinerM63SVL10,
        "M63SVL50": BTMinerM63SVL50,
        "M63SVL60": BTMinerM63SVL60,
        "M63VK10": BTMinerM63VK10,
        "M63VK20": BTMinerM63VK20,
        "M63VK30": BTMinerM63VK30,
        "M63VL10": BTMinerM63VL10,
        "M63VL30": BTMinerM63VL30,
        "M64SVL30": BTMinerM64SVL30,
        "M64VL30": BTMinerM64VL30,
        "M64VL40": BTMinerM64VL40,
        "M65S+VK30": BTMinerM65SPlusVK30,
        "M65SVK20": BTMinerM65SVK20,
        "M65SVL60": BTMinerM65SVL60,
        "M66S++VL20": BTMinerM66SPlusPlusVL20,
        "M66S+VK30": BTMinerM66SPlusVK30,
        "M66S+VL10": BTMinerM66SPlusVL10,
        "M66S+VL20": BTMinerM66SPlusVL20,
        "M66S+VL30": BTMinerM66SPlusVL30,
        "M66S+VL40": BTMinerM66SPlusVL40,
        "M66S+VL60": BTMinerM66SPlusVL60,
        "M66SVK20": BTMinerM66SVK20,
        "M66SVK30": BTMinerM66SVK30,
        "M66SVK40": BTMinerM66SVK40,
        "M66SVK50": BTMinerM66SVK50,
        "M66SVK60": BTMinerM66SVK60,
        "M66SVL10": BTMinerM66SVL10,
        "M66SVL20": BTMinerM66SVL20,
        "M66SVL30": BTMinerM66SVL30,
        "M66SVL40": BTMinerM66SVL40,
        "M66SVL50": BTMinerM66SVL50,
        "M66VK20": BTMinerM66VK20,
        "M66VK30": BTMinerM66VK30,
        "M66VL20": BTMinerM66VL20,
        "M66VL30": BTMinerM66VL30,
        "M67SVK30": BTMinerM67SVK30,
        "M70VM30": BTMinerM70VM30,
    },
    MinerTypes.AVALONMINER: {
        None: type("AvalonUnknown", (AvalonMiner, AvalonMinerMake), {}),
        "AVALONMINER 721": CGMinerAvalon721,
        "AVALONMINER 741": CGMinerAvalon741,
        "AVALONMINER 761": CGMinerAvalon761,
        "AVALONMINER 821": CGMinerAvalon821,
        "AVALONMINER 841": CGMinerAvalon841,
        "AVALONMINER 851": CGMinerAvalon851,
        "AVALONMINER 921": CGMinerAvalon921,
        "AVALONMINER 1026": CGMinerAvalon1026,
        "AVALONMINER 1047": CGMinerAvalon1047,
        "AVALONMINER 1066": CGMinerAvalon1066,
        "AVALONMINER 1126PRO": CGMinerAvalon1126Pro,
        "AVALONMINER 1166PRO": CGMinerAvalon1166Pro,
        "AVALONMINER 1246": CGMinerAvalon1246,
        "AVALONMINER NANO3": CGMinerAvalonNano3,
    },
    MinerTypes.INNOSILICON: {
        None: type("InnosiliconUnknown", (Innosilicon, InnosiliconMake), {}),
        "T3H+": InnosiliconT3HPlus,
        "A10X": InnosiliconA10X,
        "A11": InnosiliconA11,
        "A11MX": InnosiliconA11MX,
    },
    MinerTypes.GOLDSHELL: {
        None: type("GoldshellUnknown", (GoldshellMiner, GoldshellMake), {}),
        "GOLDSHELL CK5": GoldshellCK5,
        "GOLDSHELL HS5": GoldshellHS5,
        "GOLDSHELL KD5": GoldshellKD5,
        "GOLDSHELL KDMAX": GoldshellKDMax,
        "GOLDSHELL KDBOXII": GoldshellKDBoxII,
        "GOLDSHELL KDBOXPRO": GoldshellKDBoxPro,
    },
    MinerTypes.BRAIINS_OS: {
        None: BOSMiner,
        "ANTMINER S9": BOSMinerS9,
        "ANTMINER S17": BOSMinerS17,
        "ANTMINER S17+": BOSMinerS17Plus,
        "ANTMINER S17 PRO": BOSMinerS17Pro,
        "ANTMINER S17E": BOSMinerS17e,
        "ANTMINER T17": BOSMinerT17,
        "ANTMINER T17+": BOSMinerT17Plus,
        "ANTMINER T17E": BOSMinerT17e,
        "ANTMINER S19": BOSMinerS19,
        "ANTMINER S19+": BOSMinerS19Plus,
        "ANTMINER S19 PRO": BOSMinerS19Pro,
        "ANTMINER S19A": BOSMinerS19a,
        "ANTMINER S19A Pro": BOSMinerS19aPro,
        "ANTMINER S19J": BOSMinerS19j,
        "ANTMINER S19J88NOPIC": BOSMinerS19jNoPIC,
        "ANTMINER S19J PRO": BOSMinerS19jPro,
        "ANTMINER S19J PRO NOPIC": BOSMinerS19jProNoPIC,
        "ANTMINER S19J PRO+": BOSMinerS19jProPlus,
        "ANTMINER S19J PRO PLUS": BOSMinerS19jProPlus,
        "ANTMINER S19J PRO PLUS NOPIC": BOSMinerS19jProPlusNoPIC,
        "ANTMINER S19K PRO NOPIC": BOSMinerS19kProNoPIC,
        "ANTMINER S19K PRO": BOSMinerS19kProNoPIC,
        "ANTMINER S19 XP": BOSMinerS19XP,
        "ANTMINER S19 PRO+ HYD.": BOSMinerS19ProPlusHydro,
        "ANTMINER T19": BOSMinerT19,
        "ANTMINER S21": BOSMinerS21,
        "ANTMINER S21 PRO": BOSMinerS21Pro,
        "ANTMINER T21": BOSMinerT21,
        "BRAIINS MINI MINER BMM 100": BraiinsBMM100,
        "BRAIINS MINI MINER BMM 101": BraiinsBMM101,
    },
    MinerTypes.VNISH: {
        None: VNish,
        "L3+": VnishL3Plus,
        "ANTMINER L3+": VnishL3Plus,
        "ANTMINER L7": VnishL7,
        "ANTMINER S17+": VNishS17Plus,
        "ANTMINER S17 PRO": VNishS17Pro,
        "ANTMINER S19": VNishS19,
        "ANTMINER S19NOPIC": VNishS19NoPIC,
        "ANTMINER S19 PRO": VNishS19Pro,
        "ANTMINER S19J": VNishS19j,
        "ANTMINER S19I": VNishS19i,
        "ANTMINER S19J PRO": VNishS19jPro,
        "ANTMINER S19J PRO A": VNishS19jPro,
        "ANTMINER S19J PRO BB": VNishS19jPro,
        "ANTMINER S19A": VNishS19a,
        "ANTMINER S19A PRO": VNishS19aPro,
        "ANTMINER S19 PRO HYD.": VNishS19ProHydro,
        "ANTMINER S19K PRO": VNishS19kPro,
        "ANTMINER T19": VNishT19,
        "ANTMINER T21": VNishT21,
        "ANTMINER S21": VNishS21,
    },
    MinerTypes.EPIC: {
        None: ePIC,
        "ANTMINER S19": ePICS19,
        "ANTMINER S19 PRO": ePICS19Pro,
        "ANTMINER S19J": ePICS19j,
        "ANTMINER S19J PRO": ePICS19jPro,
        "ANTMINER S19J PRO+": ePICS19jProPlus,
        "ANTMINER S19K PRO": ePICS19kPro,
        "ANTMINER S19 XP": ePICS19XP,
        "ANTMINER S21": ePICS21,
        "ANTMINER S21 PRO": ePICS21Pro,
        "ANTMINER T21": ePICT21,
        "ANTMINER S19J PRO DUAL": ePICS19jProDual,
        "BLOCKMINER 520I": ePICBlockMiner520i,
        "BLOCKMINER 720I": ePICBlockMiner720i,
    },
    MinerTypes.HIVEON: {
        None: HiveonModern,
        "ANTMINER T9": HiveonT9,
        "ANTMINER S19JPRO": HiveonS19jPro,
        "ANTMINER S19": HiveonS19,
    },
    MinerTypes.LUX_OS: {
        None: LUXMiner,
        "ANTMINER S9": LUXMinerS9,
        "ANTMINER S19": LUXMinerS19,
        "ANTMINER S19 PRO": LUXMinerS19Pro,
        "ANTMINER S19J PRO": LUXMinerS19jPro,
        "ANTMINER S19J PRO+": LUXMinerS19jProPlus,
        "ANTMINER S19K PRO": LUXMinerS19kPro,
        "ANTMINER S19 XP": LUXMinerS19XP,
        "ANTMINER T19": LUXMinerT19,
        "ANTMINER S21": LUXMinerS21,
    },
    MinerTypes.AURADINE: {
        None: type("AuradineUnknown", (Auradine, AuradineMake), {}),
        "AT1500": AuradineFluxAT1500,
        "AT2860": AuradineFluxAT2860,
        "AT2880": AuradineFluxAT2880,
        "AI2500": AuradineFluxAI2500,
        "AI3680": AuradineFluxAI3680,
        "AD2500": AuradineFluxAD2500,
        "AD3500": AuradineFluxAD3500,
    },
    MinerTypes.MARATHON: {
        None: MaraMiner,
        "ANTMINER S19": MaraS19,
        "ANTMINER S19 PRO": MaraS19Pro,
        "ANTMINER S19J": MaraS19j,
        "ANTMINER S19J88NOPIC": MaraS19jNoPIC,
        "ANTMINER S19J PRO": MaraS19jPro,
        "ANTMINER S19 XP": MaraS19XP,
        "ANTMINER S19K PRO": MaraS19KPro,
        "ANTMINER S21": MaraS21,
        "ANTMINER T21": MaraT21,
    },
    MinerTypes.BITAXE: {
        None: BitAxe,
        "BM1368": BitAxeSupra,
        "BM1366": BitAxeUltra,
        "BM1397": BitAxeMax,
        "BM1370": BitAxeGamma,
    },
    MinerTypes.LUCKYMINER: {
        None: LuckyMiner,
        "BM1366": LuckyMinerLV08,
    },
    MinerTypes.ICERIVER: {
        None: type("IceRiverUnknown", (IceRiver, IceRiverMake), {}),
        "KS0": IceRiverKS0,
        "KS1": IceRiverKS1,
        "KS2": IceRiverKS2,
        "KS3": IceRiverKS3,
        "KS3L": IceRiverKS3L,
        "KS3M": IceRiverKS3M,
        "KS5": IceRiverKS5,
        "KS5L": IceRiverKS5L,
        "KS5M": IceRiverKS5M,
    },
    MinerTypes.HAMMER: {
        None: type("HammerUnknown", (BlackMiner, HammerMake), {}),
        "HAMMER D10": HammerD10,
    },
    MinerTypes.VOLCMINER: {
        None: type("VolcMinerUnknown", (BlackMiner, VolcMinerMake), {}),
        "VOLCMINER D1": VolcMinerD1,
    },
}


async def concurrent_get_first_result(tasks: list, verification_func: Callable) -> Any:
    res = None
    for fut in asyncio.as_completed(tasks):
        res = await fut
        if verification_func(res):
            break
    for t in tasks:
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass
    return res


class MinerFactory:
    async def get_multiple_miners(
        self, ips: list[str], limit: int = 200
    ) -> list[AnyMiner]:
        results = []

        async for miner in self.get_miner_generator(ips, limit):
            results.append(miner)

        return results

    async def get_miner_generator(
        self, ips: list, limit: int = 200
    ) -> AsyncGenerator[AnyMiner]:
        tasks = []
        semaphore = asyncio.Semaphore(limit)

        for ip in ips:
            tasks.append(asyncio.create_task(self.get_miner(ip)))

        for task in tasks:
            async with semaphore:
                result = await task
                if result is not None:
                    yield result

    async def get_miner(self, ip: str | ipaddress.ip_address) -> AnyMiner | None:
        ip = str(ip)

        miner_type = None

        for _ in range(settings.get("factory_get_retries", 1)):
            task = asyncio.create_task(self._get_miner_type(ip))
            try:
                miner_type = await asyncio.wait_for(
                    task, timeout=settings.get("factory_get_timeout", 3)
                )
            except asyncio.TimeoutError:
                continue
            else:
                if miner_type is not None:
                    break

        if miner_type is not None:
            miner_model = None
            miner_model_fns = {
                MinerTypes.ANTMINER: self.get_miner_model_antminer,
                MinerTypes.WHATSMINER: self.get_miner_model_whatsminer,
                MinerTypes.AVALONMINER: self.get_miner_model_avalonminer,
                MinerTypes.INNOSILICON: self.get_miner_model_innosilicon,
                MinerTypes.GOLDSHELL: self.get_miner_model_goldshell,
                MinerTypes.BRAIINS_OS: self.get_miner_model_braiins_os,
                MinerTypes.VNISH: self.get_miner_model_vnish,
                MinerTypes.EPIC: self.get_miner_model_epic,
                MinerTypes.HIVEON: self.get_miner_model_hiveon,
                MinerTypes.LUX_OS: self.get_miner_model_luxos,
                MinerTypes.AURADINE: self.get_miner_model_auradine,
                MinerTypes.MARATHON: self.get_miner_model_marathon,
                MinerTypes.BITAXE: self.get_miner_model_bitaxe,
                MinerTypes.LUCKYMINER: self.get_miner_model_luckyminer,
                MinerTypes.ICERIVER: self.get_miner_model_iceriver,
                MinerTypes.HAMMER: self.get_miner_model_hammer,
                MinerTypes.VOLCMINER: self.get_miner_model_volcminer,
            }
            fn = miner_model_fns.get(miner_type)

            if fn is not None:
                # noinspection PyArgumentList
                task = asyncio.create_task(fn(ip))
                try:
                    miner_model = await asyncio.wait_for(
                        task, timeout=settings.get("factory_get_timeout", 3)
                    )
                except asyncio.TimeoutError:
                    pass
            miner = self._select_miner_from_classes(
                ip,
                miner_type=miner_type,
                miner_model=miner_model,
            )
            return miner

    async def _get_miner_type(self, ip: str) -> MinerTypes | None:
        tasks = [
            asyncio.create_task(self._get_miner_web(ip)),
            asyncio.create_task(self._get_miner_socket(ip)),
        ]

        return await concurrent_get_first_result(tasks, lambda x: x is not None)

    async def _get_miner_web(self, ip: str) -> MinerTypes | None:
        urls = [f"http://{ip}/", f"https://{ip}/"]
        async with httpx.AsyncClient(
            transport=settings.transport(verify=False)
        ) as session:
            tasks = [asyncio.create_task(self._web_ping(session, url)) for url in urls]

            text, resp = await concurrent_get_first_result(
                tasks,
                lambda x: x[0] is not None
                and self._parse_web_type(x[0], x[1]) is not None,
            )
            if text is not None:
                mtype = self._parse_web_type(text, resp)
                if mtype == MinerTypes.ANTMINER:
                    # could still be mara
                    auth = httpx.DigestAuth("root", "root")
                    res = await self.send_web_command(ip, "/kaonsu/v1/brief", auth=auth)
                    if res is not None:
                        mtype = MinerTypes.MARATHON
                if mtype == MinerTypes.HAMMER:
                    res = await self.get_miner_model_hammer(ip)
                    if res is None:
                        return MinerTypes.HAMMER
                    if "HAMMER" in res.upper():
                        mtype = MinerTypes.HAMMER
                    else:
                        mtype = MinerTypes.VOLCMINER
                return mtype

    @staticmethod
    async def _web_ping(
        session: httpx.AsyncClient, url: str
    ) -> tuple[str | None, httpx.Response | None]:
        try:
            resp = await session.get(url, follow_redirects=True)
            return resp.text, resp
        except (
            httpx.HTTPError,
            asyncio.TimeoutError,
            anyio.EndOfStream,
            anyio.ClosedResourceError,
        ):
            pass
        return None, None

    @staticmethod
    def _parse_web_type(web_text: str, web_resp: httpx.Response) -> MinerTypes | None:
        if web_resp.status_code == 401 and 'realm="antMiner' in web_resp.headers.get(
            "www-authenticate", ""
        ):
            return MinerTypes.ANTMINER
        if web_resp.status_code == 401 and 'realm="blackMiner' in web_resp.headers.get(
            "www-authenticate", ""
        ):
            return MinerTypes.HAMMER
        if len(web_resp.history) > 0:
            history_resp = web_resp.history[0]
            if (
                "/cgi-bin/luci" in web_text
                and history_resp.status_code == 307
                and "https://" in history_resp.headers.get("location", "")
            ):
                return MinerTypes.WHATSMINER
        if "Braiins OS" in web_text:
            return MinerTypes.BRAIINS_OS
        if "Luxor Firmware" in web_text:
            return MinerTypes.LUX_OS
        if "<TITLE>用户界面</TITLE>" in web_text:
            return MinerTypes.ICERIVER
        if "AxeOS" in web_text:
            return MinerTypes.BITAXE
        if "Lucky miner" in web_text:
            return MinerTypes.LUCKYMINER
        if "cloud-box" in web_text:
            return MinerTypes.GOLDSHELL
        if "AnthillOS" in web_text:
            return MinerTypes.VNISH
        if "Miner Web Dashboard" in web_text:
            return MinerTypes.EPIC
        if "Avalon" in web_text:
            return MinerTypes.AVALONMINER
        if "DragonMint" in web_text:
            return MinerTypes.INNOSILICON
        if "Miner UI" in web_text:
            return MinerTypes.AURADINE

    async def _get_miner_socket(self, ip: str) -> MinerTypes | None:
        commands = ["version", "devdetails"]
        tasks = [asyncio.create_task(self._socket_ping(ip, cmd)) for cmd in commands]

        data = await concurrent_get_first_result(
            tasks,
            lambda x: x is not None and self._parse_socket_type(x) is not None,
        )
        if data is not None:
            d = self._parse_socket_type(data)
            return d

    @staticmethod
    async def _socket_ping(ip: str, cmd: str) -> str | None:
        data = b""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(str(ip), 4028),
                timeout=settings.get("factory_get_timeout", 3),
            )
        except (ConnectionError, OSError, asyncio.TimeoutError):
            return

        cmd = {"command": cmd}

        try:
            # send the command
            writer.write(json.dumps(cmd).encode("utf-8"))
            await writer.drain()

            # loop to receive all the data
            timeouts_remaining = max(1, int(settings.get("factory_get_timeout", 3)))
            while True:
                try:
                    d = await asyncio.wait_for(reader.read(4096), timeout=1)
                    if not d:
                        break
                    data += d
                except asyncio.TimeoutError:
                    timeouts_remaining -= 1
                    if not timeouts_remaining:
                        logger.warning(f"{ip}: Socket ping timeout.")
                        break
                except ConnectionResetError:
                    return
        except asyncio.CancelledError:
            raise
        except (ConnectionError, OSError):
            return
        finally:
            # Handle cancellation explicitly
            if writer.transport.is_closing():
                writer.transport.close()
            else:
                writer.close()
            try:
                await writer.wait_closed()
            except (ConnectionError, OSError):
                return
        if data:
            return data.decode("utf-8")

    @staticmethod
    def _parse_socket_type(data: str) -> MinerTypes | None:
        upper_data = data.upper()
        if "BOSMINER" in upper_data or "BOSER" in upper_data:
            return MinerTypes.BRAIINS_OS
        if "BTMINER" in upper_data or "BITMICRO" in upper_data:
            return MinerTypes.WHATSMINER
        if "LUXMINER" in upper_data:
            return MinerTypes.LUX_OS
        if "HIVEON" in upper_data:
            return MinerTypes.HIVEON
        if "KAONSU" in upper_data:
            return MinerTypes.MARATHON
        if "ANTMINER" in upper_data and "DEVDETAILS" not in upper_data:
            return MinerTypes.ANTMINER
        if (
            "INTCHAINS_QOMO" in upper_data
            or "KDAMINER" in upper_data
            or "BFGMINER" in upper_data
        ):
            return MinerTypes.GOLDSHELL
        if "INNOMINER" in upper_data:
            return MinerTypes.INNOSILICON
        if "AVALON" in upper_data:
            return MinerTypes.AVALONMINER
        if "GCMINER" in upper_data or "FLUXOS" in upper_data:
            return MinerTypes.AURADINE
        if "VNISH" in upper_data:
            return MinerTypes.VNISH

    async def send_web_command(
        self,
        ip: str,
        location: str,
        auth: httpx.DigestAuth = None,
    ) -> dict | None:
        async with httpx.AsyncClient(transport=settings.transport()) as session:
            try:
                data = await session.get(
                    f"http://{ip}{location}",
                    auth=auth,
                    timeout=settings.get("factory_get_timeout", 3),
                )
            except (httpx.HTTPError, asyncio.TimeoutError):
                logger.info(f"{ip}: Web command timeout.")
                return
        if data is None:
            return
        try:
            json_data = data.json()
        except (json.JSONDecodeError, asyncio.TimeoutError):
            try:
                return json.loads(data.text)
            except (json.JSONDecodeError, httpx.HTTPError):
                return
        else:
            return json_data

    async def send_api_command(self, ip: str, command: str) -> dict | None:
        data = b""
        try:
            reader, writer = await asyncio.open_connection(ip, 4028)
        except (ConnectionError, OSError):
            return
        cmd = {"command": command}

        try:
            # send the command
            writer.write(json.dumps(cmd).encode("utf-8"))
            await writer.drain()

            # loop to receive all the data
            while True:
                d = await reader.read(4096)
                if not d:
                    break
                data += d

            writer.close()
            await writer.wait_closed()
        except asyncio.CancelledError:
            writer.close()
            await writer.wait_closed()
            return
        except (ConnectionError, OSError):
            return
        if data == b"Socket connect failed: Connection refused\n":
            return

        data = await self._fix_api_data(data)

        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return {}

        return data

    @staticmethod
    async def _fix_api_data(data: bytes) -> str:
        if data.endswith(b"\x00"):
            str_data = data.decode("utf-8")[:-1]
        else:
            str_data = data.decode("utf-8")
        # fix an error with a btminer return having an extra comma that breaks json.loads()
        str_data = str_data.replace(",}", "}")
        # fix an error with a btminer return having a newline that breaks json.loads()
        str_data = str_data.replace("\n", "")
        # fix an error with a bmminer return not having a specific comma that breaks json.loads()
        str_data = str_data.replace("}{", "},{")
        # fix an error with a bmminer return having a specific comma that breaks json.loads()
        str_data = str_data.replace("[,{", "[{")
        # fix an error with a btminer return having a missing comma. (2023-01-06 version)
        str_data = str_data.replace('""temp0', '","temp0')
        # fix an error with Avalonminers returning inf and nan
        str_data = str_data.replace('"inf"', "0")
        str_data = str_data.replace('"nan"', "0")
        # fix whatever this garbage from avalonminers is `,"id":1}`
        if str_data.startswith(","):
            str_data = f"{{{str_data[1:]}"
        # try to fix an error with overflowing the recieve buffer
        # this can happen in cases such as bugged btminers returning arbitrary length error info with 100s of errors.
        if not str_data.endswith("}"):
            str_data = ",".join(str_data.split(",")[:-1]) + "}"

        # fix a really nasty bug with whatsminer API v2.0.4 where they return a list structured like a dict
        if re.search(r"\"error_code\":\[\".+\"]", str_data):
            str_data = str_data.replace("[", "{").replace("]", "}")

        return str_data

    @staticmethod
    def _select_miner_from_classes(
        ip: ipaddress.ip_address,
        miner_model: str | None,
        miner_type: MinerTypes | None,
    ) -> AnyMiner | None:
        # special case since hiveon miners return web results copying the antminer stock FW
        if "HIVEON" in str(miner_model).upper():
            miner_model = str(miner_model).upper().replace(" HIVEON", "")
            miner_type = MinerTypes.HIVEON
        try:
            return MINER_CLASSES[miner_type][str(miner_model).upper()](ip)
        except LookupError:
            if miner_type in MINER_CLASSES:
                if miner_model is not None:
                    warnings.warn(
                        f"Partially supported miner found: {miner_model}, type: {miner_type}, please open an issue with miner data "
                        f"and this model on GitHub (https://github.com/UpstreamData/pyasic/issues)."
                    )
                return MINER_CLASSES[miner_type][None](ip)
            return UnknownMiner(str(ip))

    async def get_miner_model_antminer(self, ip: str) -> str | None:
        tasks = [
            asyncio.create_task(self._get_model_antminer_web(ip)),
            asyncio.create_task(self._get_model_antminer_sock(ip)),
        ]

        return await concurrent_get_first_result(tasks, lambda x: x is not None)

    async def _get_model_antminer_web(self, ip: str) -> str | None:
        # last resort, this is slow
        auth = httpx.DigestAuth(
            "root", settings.get("default_antminer_web_password", "root")
        )
        web_json_data = await self.send_web_command(
            ip, "/cgi-bin/get_system_info.cgi", auth=auth
        )

        try:
            miner_model = web_json_data["minertype"]

            return miner_model
        except (TypeError, LookupError):
            pass

    async def _get_model_antminer_sock(self, ip: str) -> str | None:
        sock_json_data = await self.send_api_command(ip, "version")
        try:
            miner_model = sock_json_data["VERSION"][0]["Type"]

            if " (" in miner_model:
                split_miner_model = miner_model.split(" (")
                miner_model = split_miner_model[0]

            return miner_model
        except (TypeError, LookupError):
            pass

        sock_json_data = await self.send_api_command(ip, "stats")
        try:
            miner_model = sock_json_data["STATS"][0]["Type"]

            if " (" in miner_model:
                split_miner_model = miner_model.split(" (")
                miner_model = split_miner_model[0]

            return miner_model
        except (TypeError, LookupError):
            pass

    async def get_miner_model_goldshell(self, ip: str) -> str | None:
        json_data = await self.send_web_command(ip, "/mcb/status")

        try:
            miner_model = json_data["model"].replace("-", " ")

            return miner_model
        except (TypeError, LookupError):
            pass

    async def get_miner_model_whatsminer(self, ip: str) -> str | None:
        sock_json_data = await self.send_api_command(ip, "devdetails")
        try:
            miner_model = sock_json_data["DEVDETAILS"][0]["Model"].replace("_", "")
            miner_model = miner_model[:-1] + "0"

            return miner_model
        except (TypeError, LookupError):
            pass

    async def get_miner_model_avalonminer(self, ip: str) -> str | None:
        sock_json_data = await self.send_api_command(ip, "version")
        try:
            miner_model = sock_json_data["VERSION"][0]["PROD"].upper()
            if "-" in miner_model:
                miner_model = miner_model.split("-")[0]
            if miner_model in ["AVALONNANO", "AVALON0O"]:
                nano_subtype = sock_json_data["VERSION"][0]["MODEL"].upper()
                miner_model = f"AVALONMINER {nano_subtype}"
            return miner_model
        except (TypeError, LookupError):
            pass

    async def get_miner_model_innosilicon(self, ip: str) -> str | None:
        try:
            async with httpx.AsyncClient(transport=settings.transport()) as session:
                auth_req = await session.post(
                    f"http://{ip}/api/auth",
                    data={
                        "username": "admin",
                        "password": settings.get(
                            "default_innosilicon_web_password", "admin"
                        ),
                    },
                )
                auth = auth_req.json()["jwt"]
        except (httpx.HTTPError, LookupError):
            return

        try:
            async with httpx.AsyncClient(transport=settings.transport()) as session:
                web_data = (
                    await session.post(
                        f"http://{ip}/api/type",
                        headers={"Authorization": "Bearer " + auth},
                        data={},
                    )
                ).json()
                return web_data["type"]
        except (httpx.HTTPError, LookupError):
            pass
        try:
            async with httpx.AsyncClient(transport=settings.transport()) as session:
                web_data = (
                    await session.post(
                        f"http://{ip}/overview",
                        headers={"Authorization": "Bearer " + auth},
                        data={},
                    )
                ).json()
                return web_data["type"]
        except (httpx.HTTPError, LookupError):
            pass

    async def get_miner_model_braiins_os(self, ip: str) -> str | None:
        sock_json_data = await self.send_api_command(ip, "devdetails")
        try:
            miner_model = (
                sock_json_data["DEVDETAILS"][0]["Model"]
                .replace("Bitmain ", "")
                .replace("S19XP", "S19 XP")
            )
            return miner_model
        except (TypeError, LookupError):
            pass

        try:
            async with httpx.AsyncClient(transport=settings.transport()) as session:
                d = await session.post(
                    f"http://{ip}/graphql",
                    json={"query": "{bosminer {info{modelName}}}"},
                )
            if d.status_code == 200:
                json_data = d.json()
                miner_model = json_data["data"]["bosminer"]["info"][
                    "modelName"
                ].replace("S19XP", "S19 XP")
                return miner_model
        except (httpx.HTTPError, LookupError):
            pass

    async def get_miner_model_vnish(self, ip: str) -> str | None:
        sock_json_data = await self.send_api_command(ip, "stats")
        try:
            miner_model = sock_json_data["STATS"][0]["Type"]
            if " (" in miner_model:
                split_miner_model = miner_model.split(" (")
                miner_model = split_miner_model[0]

            if "(88)" in miner_model:
                miner_model = miner_model.replace("(88)", "NOPIC")

            if " AML" in miner_model:
                miner_model = miner_model.replace(" AML", "")

            return miner_model
        except (TypeError, LookupError):
            pass

    async def get_miner_model_epic(self, ip: str) -> str | None:
        for retry_cnt in range(settings.get("get_data_retries", 1)):
            sock_json_data = await self.send_web_command(ip, ":4028/capabilities")
            try:
                miner_model = sock_json_data["Model"]
                return miner_model
            except (TypeError, LookupError):
                if retry_cnt < settings.get("get_data_retries", 1) - 1:
                    continue
                else:
                    pass

    async def get_miner_model_hiveon(self, ip: str) -> str | None:
        sock_json_data = await self.send_api_command(ip, "version")
        try:
            miner_type = sock_json_data["VERSION"][0]["Type"]

            return miner_type.replace(" HIVEON", "")
        except (TypeError, LookupError):
            pass

    async def get_miner_model_luxos(self, ip: str) -> str | None:
        sock_json_data = await self.send_api_command(ip, "version")
        try:
            miner_model = sock_json_data["VERSION"][0]["Type"]

            if " (" in miner_model:
                split_miner_model = miner_model.split(" (")
                miner_model = split_miner_model[0]
            return miner_model
        except (TypeError, LookupError):
            pass

    async def get_miner_model_auradine(self, ip: str) -> str | None:
        sock_json_data = await self.send_api_command(ip, "devdetails")
        try:
            return sock_json_data["DEVDETAILS"][0]["Model"]
        except LookupError:
            pass

    async def get_miner_model_marathon(self, ip: str) -> str | None:
        auth = httpx.DigestAuth("root", "root")
        web_json_data = await self.send_web_command(
            ip, "/kaonsu/v1/overview", auth=auth
        )

        try:
            miner_model = web_json_data["model"]
            if miner_model == "":
                return None

            return miner_model
        except (TypeError, LookupError):
            pass

    async def get_miner_model_bitaxe(self, ip: str) -> str | None:
        web_json_data = await self.send_web_command(ip, "/api/system/info")

        try:
            miner_model = web_json_data["ASICModel"]
            if miner_model == "":
                return None

            return miner_model
        except (TypeError, LookupError):
            pass

    async def get_miner_model_luckyminer(self, ip: str) -> str | None:
        web_json_data = await self.send_web_command(ip, "/api/system/info")

        try:
            miner_model = web_json_data["ASICModel"]
            if miner_model == "":
                return None

            return miner_model
        except (TypeError, LookupError):
            pass

    async def get_miner_model_iceriver(self, ip: str) -> str | None:
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            try:
                # auth
                await client.post(
                    f"http://{ip}/user/loginpost",
                    params={
                        "post": "6",
                        "user": "admin",
                        "pwd": settings.get(
                            "default_iceriver_web_password", "12345678"
                        ),
                    },
                )
            except httpx.HTTPError:
                return None
            try:
                resp = await client.post(
                    f"http://{ip}:/user/userpanel", params={"post": "4"}
                )
                if not resp.status_code == 200:
                    return
                result = resp.json()
                software_ver = result["data"]["softver1"]
                split_ver = software_ver.split("_")
                if split_ver[-1] == "miner":
                    miner_ver = split_ver[-2]
                else:
                    miner_ver = split_ver[-1].replace("miner", "")
                return miner_ver.upper()
            except httpx.HTTPError:
                pass

    async def get_miner_model_hammer(self, ip: str) -> str | None:
        auth = httpx.DigestAuth(
            "root", settings.get("default_hammer_web_password", "root")
        )
        web_json_data = await self.send_web_command(
            ip, "/cgi-bin/get_system_info.cgi", auth=auth
        )

        try:
            miner_model = web_json_data["minertype"]

            return miner_model
        except (TypeError, LookupError):
            pass

    async def get_miner_model_volcminer(self, ip: str) -> str | None:
        auth = httpx.DigestAuth(
            "root", settings.get("default_volcminer_web_password", "root")
        )
        web_json_data = await self.send_web_command(
            ip, "/cgi-bin/get_system_info.cgi", auth=auth
        )

        try:
            miner_model = web_json_data["minertype"]

            return miner_model
        except (TypeError, LookupError):
            pass


miner_factory = MinerFactory()


# abstracted version of get miner that is easier to access
async def get_miner(ip: ipaddress.ip_address | str) -> AnyMiner:
    return await miner_factory.get_miner(ip)
