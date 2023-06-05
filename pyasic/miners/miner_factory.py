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


import asyncio
import ipaddress
import json
import re
from ipaddress import IPv4Address
from typing import Optional, Tuple, Union

import httpx

from pyasic.logger import logger
from pyasic.miners.backends import BOSMiner  # noqa - Ignore _module import
from pyasic.miners.backends import CGMiner  # noqa - Ignore _module import
from pyasic.miners.backends.bmminer import BMMiner  # noqa - Ignore _module import
from pyasic.miners.backends.bosminer_old import (  # noqa - Ignore _module import
    BOSMinerOld,
)
from pyasic.miners.backends.btminer import BTMiner  # noqa - Ignore _module import
from pyasic.miners.base import AnyMiner
from pyasic.miners.btc import *
from pyasic.miners.ckb import *
from pyasic.miners.dcr import *
from pyasic.miners.dsh import *
from pyasic.miners.etc import *
from pyasic.miners.hns import *
from pyasic.miners.kda import *
from pyasic.miners.ltc import *
from pyasic.miners.unknown import UnknownMiner
from pyasic.miners.zec import *

TIMEOUT = 30
LOOPS = 1


MINER_CLASSES = {
    "ANTMINER DR5": {
        "Default": CGMinerDR5,
        "CGMiner": CGMinerDR5,
    },
    "ANTMINER D3": {
        "Default": CGMinerD3,
        "CGMiner": CGMinerD3,
    },
    "ANTMINER HS3": {
        "Default": CGMinerHS3,
        "CGMiner": CGMinerHS3,
    },
    "ANTMINER L3+": {
        "Default": BMMinerL3Plus,
        "BMMiner": BMMinerL3Plus,
        "VNish": VnishL3Plus,
    },
    "ANTMINER L7": {
        "Default": BMMinerL7,
        "BMMiner": BMMinerL7,
    },
    "ANTMINER E9 PRO": {
        "Default": CGMinerE9Pro,
        "BMMiner": CGMinerE9Pro,
    },
    "ANTMINER S9": {
        "Default": BOSMinerS9,
        "BOSMiner": BOSMinerOld,
        "BOSMiner+": BOSMinerS9,
        "BMMiner": BMMinerS9,
        "CGMiner": CGMinerS9,
    },
    "ANTMINER S9I": {
        "Default": BMMinerS9i,
        "BMMiner": BMMinerS9i,
    },
    "ANTMINER S9J": {
        "Default": BMMinerS9j,
        "BMMiner": BMMinerS9j,
    },
    "ANTMINER T9": {
        "Default": BMMinerT9,
        "BMMiner": BMMinerT9,
        "Hiveon": HiveonT9,
        "CGMiner": CGMinerT9,
    },
    "ANTMINER Z15": {
        "Default": CGMinerZ15,
        "CGMiner": CGMinerZ15,
    },
    "ANTMINER S17": {
        "Default": BMMinerS17,
        "BOSMiner+": BOSMinerS17,
        "BMMiner": BMMinerS17,
        "CGMiner": CGMinerS17,
    },
    "ANTMINER S17+": {
        "Default": BMMinerS17Plus,
        "BOSMiner+": BOSMinerS17Plus,
        "BMMiner": BMMinerS17Plus,
        "CGMiner": CGMinerS17Plus,
    },
    "ANTMINER S17 PRO": {
        "Default": BMMinerS17Pro,
        "BOSMiner+": BOSMinerS17Pro,
        "BMMiner": BMMinerS17Pro,
        "CGMiner": CGMinerS17Pro,
    },
    "ANTMINER S17E": {
        "Default": BMMinerS17e,
        "BOSMiner+": BOSMinerS17e,
        "BMMiner": BMMinerS17e,
        "CGMiner": CGMinerS17e,
    },
    "ANTMINER T17": {
        "Default": BMMinerT17,
        "BOSMiner+": BOSMinerT17,
        "BMMiner": BMMinerT17,
        "CGMiner": CGMinerT17,
    },
    "ANTMINER T17+": {
        "Default": BMMinerT17Plus,
        "BOSMiner+": BOSMinerT17Plus,
        "BMMiner": BMMinerT17Plus,
        "CGMiner": CGMinerT17Plus,
    },
    "ANTMINER T17E": {
        "Default": BMMinerT17e,
        "BOSMiner+": BOSMinerT17e,
        "BMMiner": BMMinerT17e,
        "CGMiner": CGMinerT17e,
    },
    "ANTMINER S19": {
        "Default": BMMinerS19,
        "BOSMiner+": BOSMinerS19,
        "BMMiner": BMMinerS19,
        "CGMiner": CGMinerS19,
        "VNish": VNishS19,
    },
    "ANTMINER S19L": {
        "Default": BMMinerS19L,
        "BMMiner": BMMinerS19L,
    },
    "ANTMINER S19 PRO": {
        "Default": BMMinerS19Pro,
        "BOSMiner+": BOSMinerS19Pro,
        "BMMiner": BMMinerS19Pro,
        "CGMiner": CGMinerS19Pro,
        "VNish": VNishS19Pro,
    },
    "ANTMINER S19J": {
        "Default": BMMinerS19j,
        "BOSMiner+": BOSMinerS19j,
        "BMMiner": BMMinerS19j,
        "CGMiner": CGMinerS19j,
        "VNish": VNishS19j,
    },
    "ANTMINER S19J NOPIC": {
        "Default": BMMinerS19jNoPIC,
        "BOSMiner+": BOSMinerS19jNoPIC,
        "BMMiner": BMMinerS19jNoPIC,
    },
    "ANTMINER S19PRO+": {
        "Default": BMMinerS19ProPlus,
        "BMMiner": BMMinerS19ProPlus,
    },
    "ANTMINER S19J PRO": {
        "Default": BMMinerS19jPro,
        "BOSMiner+": BOSMinerS19jPro,
        "BMMiner": BMMinerS19jPro,
        "CGMiner": CGMinerS19jPro,
        "VNish": VNishS19jPro,
    },
    "ANTMINER S19 XP": {
        "Default": BMMinerS19XP,
        "BMMiner": BMMinerS19XP,
    },
    "ANTMINER S19A": {
        "Default": BMMinerS19a,
        "BMMiner": BMMinerS19a,
        "VNish": VNishS19a,
    },
    "ANTMINER S19A PRO": {
        "Default": BMMinerS19aPro,
        "BMMiner": BMMinerS19aPro,
        "VNish": VNishS19aPro,
    },
    "ANTMINER T19": {
        "Default": BMMinerT19,
        "BOSMiner+": BOSMinerT19,
        "BMMiner": BMMinerT19,
        "CGMiner": CGMinerT19,
        "VNish": VNishT19,
    },
    "GOLDSHELL CK5": {
        "Default": BFGMinerCK5,
        "BFGMiner": BFGMinerCK5,
        "CGMiner": BFGMinerCK5,
    },
    "GOLDSHELL HS5": {
        "Default": BFGMinerHS5,
        "BFGMiner": BFGMinerHS5,
        "CGMiner": BFGMinerHS5,
    },
    "GOLDSHELL KD5": {
        "Default": BFGMinerKD5,
        "BFGMiner": BFGMinerKD5,
        "CGMiner": BFGMinerKD5,
    },
    "GOLDSHELL KDMAX": {
        "Default": BFGMinerKDMax,
        "BFGMiner": BFGMinerKDMax,
        "CGMiner": BFGMinerKDMax,
    },
    "M20": {"Default": BTMinerM20V10, "BTMiner": BTMinerM20V10, "10": BTMinerM20V10},
    "M20S": {
        "Default": BTMinerM20SV10,
        "BTMiner": BTMinerM20SV10,
        "10": BTMinerM20SV10,
        "20": BTMinerM20SV20,
        "30": BTMinerM20SV30,
    },
    "M20S+": {
        "Default": BTMinerM20SPlusV30,
        "BTMiner": BTMinerM20SPlusV30,
        "30": BTMinerM20SPlusV30,
    },
    "M21": {"Default": BTMinerM21V10, "BTMiner": BTMinerM21V10, "10": BTMinerM21V10},
    "M21S": {
        "Default": BTMinerM21SV20,
        "BTMiner": BTMinerM21SV20,
        "20": BTMinerM21SV20,
        "60": BTMinerM21SV60,
        "70": BTMinerM21SV70,
    },
    "M21S+": {
        "Default": BTMinerM21SPlusV20,
        "BTMiner": BTMinerM21SPlusV20,
        "20": BTMinerM21SPlusV20,
    },
    "M29": {"Default": BTMinerM29V10, "BTMiner": BTMinerM29V10, "10": BTMinerM29V10},
    "M30": {
        "Default": BTMinerM30V10,
        "BTMiner": BTMinerM30V10,
        "10": BTMinerM30V10,
        "20": BTMinerM30V20,
    },
    "M30S": {
        "Default": BTMinerM30SV10,
        "BTMiner": BTMinerM30SV10,
        "10": BTMinerM30SV10,
        "20": BTMinerM30SV20,
        "30": BTMinerM30SV30,
        "40": BTMinerM30SV40,
        "50": BTMinerM30SV50,
        "60": BTMinerM30SV60,
        "70": BTMinerM30SV70,
        "80": BTMinerM30SV80,
        "E10": BTMinerM30SVE10,
        "E20": BTMinerM30SVE20,
        "E30": BTMinerM30SVE30,
        "E40": BTMinerM30SVE40,
        "E50": BTMinerM30SVE50,
        "E60": BTMinerM30SVE60,
        "E70": BTMinerM30SVE70,
        "F10": BTMinerM30SVF10,
        "F20": BTMinerM30SVF20,
        "F30": BTMinerM30SVF30,
        "G10": BTMinerM30SVG10,
        "G20": BTMinerM30SVG20,
        "G30": BTMinerM30SVG30,
        "G40": BTMinerM30SVG40,
        "H10": BTMinerM30SVH10,
        "H20": BTMinerM30SVH20,
        "H30": BTMinerM30SVH30,
        "H40": BTMinerM30SVH40,
        "H50": BTMinerM30SVH50,
        "H60": BTMinerM30SVH60,
        "I20": BTMinerM30SVI20,
    },
    "M30S+": {
        "Default": BTMinerM30SPlusV10,
        "BTMiner": BTMinerM30SPlusV10,
        "10": BTMinerM30SPlusV10,
        "20": BTMinerM30SPlusV20,
        "30": BTMinerM30SPlusV30,
        "40": BTMinerM30SPlusV40,
        "50": BTMinerM30SPlusV50,
        "60": BTMinerM30SPlusV60,
        "70": BTMinerM30SPlusV70,
        "80": BTMinerM30SPlusV80,
        "90": BTMinerM30SPlusV90,
        "100": BTMinerM30SPlusV100,
        "E30": BTMinerM30SPlusVE30,
        "E40": BTMinerM30SPlusVE40,
        "E50": BTMinerM30SPlusVE50,
        "E60": BTMinerM30SPlusVE60,
        "E70": BTMinerM30SPlusVE70,
        "E80": BTMinerM30SPlusVE80,
        "E90": BTMinerM30SPlusVE90,
        "E100": BTMinerM30SPlusVE100,
        "F20": BTMinerM30SPlusVF20,
        "F30": BTMinerM30SPlusVF30,
        "G30": BTMinerM30SPlusVG30,
        "G40": BTMinerM30SPlusVG40,
        "G50": BTMinerM30SPlusVG50,
        "G60": BTMinerM30SPlusVG60,
        "H10": BTMinerM30SPlusVH10,
        "H20": BTMinerM30SPlusVH20,
        "H30": BTMinerM30SPlusVH30,
        "H40": BTMinerM30SPlusVH40,
        "H50": BTMinerM30SPlusVH50,
        "H60": BTMinerM30SPlusVH60,
    },
    "M30S++": {
        "Default": BTMinerM30SPlusPlusV10,
        "BTMiner": BTMinerM30SPlusPlusV10,
        "10": BTMinerM30SPlusPlusV10,
        "20": BTMinerM30SPlusPlusV20,
        "E30": BTMinerM30SPlusPlusVE30,
        "E40": BTMinerM30SPlusPlusVE40,
        "E50": BTMinerM30SPlusPlusVE50,
        "F40": BTMinerM30SPlusPlusVF40,
        "G30": BTMinerM30SPlusPlusVG30,
        "G40": BTMinerM30SPlusPlusVG40,
        "G50": BTMinerM30SPlusPlusVG50,
        "H10": BTMinerM30SPlusPlusVH10,
        "H20": BTMinerM30SPlusPlusVH20,
        "H30": BTMinerM30SPlusPlusVH30,
        "H40": BTMinerM30SPlusPlusVH40,
        "H50": BTMinerM30SPlusPlusVH50,
        "H60": BTMinerM30SPlusPlusVH60,
        "H70": BTMinerM30SPlusPlusVH70,
        "H80": BTMinerM30SPlusPlusVH80,
        "H90": BTMinerM30SPlusPlusVH90,
        "H100": BTMinerM30SPlusPlusVH100,
        "J20": BTMinerM30SPlusPlusVJ20,
        "J30": BTMinerM30SPlusPlusVJ30,
    },
    "M31": {
        "Default": BTMinerM31V10,
        "BTMiner": BTMinerM31V10,
        "10": BTMinerM31V10,
        "20": BTMinerM31V20,
    },
    "M31S": {
        "Default": BTMinerM31SV10,
        "BTMiner": BTMinerM31SV10,
        "10": BTMinerM31SV10,
        "20": BTMinerM31SV20,
        "30": BTMinerM31SV30,
        "40": BTMinerM31SV40,
        "50": BTMinerM31SV50,
        "60": BTMinerM31SV60,
        "70": BTMinerM31SV70,
        "80": BTMinerM31SV80,
        "90": BTMinerM31SV90,
        "E10": BTMinerM31SVE10,
        "E20": BTMinerM31SVE20,
        "E30": BTMinerM31SVE30,
    },
    "M31SE": {
        "Default": BTMinerM31SEV10,
        "BTMiner": BTMinerM31SEV10,
        "10": BTMinerM31SEV10,
        "20": BTMinerM31SEV20,
        "30": BTMinerM31SEV30,
    },
    "M31H": {
        "Default": BTMinerM31HV40,
        "BTMiner": BTMinerM31HV40,
        "40": BTMinerM31HV40,
    },
    "M31S+": {
        "Default": BTMinerM31SPlusV10,
        "BTMiner": BTMinerM31SPlusV10,
        "10": BTMinerM31SPlusV10,
        "20": BTMinerM31SPlusV20,
        "30": BTMinerM31SPlusV30,
        "40": BTMinerM31SPlusV40,
        "50": BTMinerM31SPlusV50,
        "60": BTMinerM31SPlusV60,
        "80": BTMinerM31SPlusV80,
        "90": BTMinerM31SPlusV90,
        "100": BTMinerM31SPlusV100,
        "E10": BTMinerM31SPlusVE10,
        "E20": BTMinerM31SPlusVE20,
        "E30": BTMinerM31SPlusVE30,
        "E40": BTMinerM31SPlusVE40,
        "E50": BTMinerM31SPlusVE50,
        "E60": BTMinerM31SPlusVE60,
        "E80": BTMinerM31SPlusVE80,
        "F20": BTMinerM31SPlusVF20,
        "F30": BTMinerM31SPlusVF30,
        "G20": BTMinerM31SPlusVG20,
        "G30": BTMinerM31SPlusVG30,
    },
    "M32": {
        "Default": BTMinerM32V10,
        "BTMiner": BTMinerM32V10,
        "10": BTMinerM32V10,
        "20": BTMinerM32V20,
    },
    "M32S": {
        "Default": BTMinerM32S,
        "BTMiner": BTMinerM32S,
    },
    "M33": {
        "Default": BTMinerM33V10,
        "BTMiner": BTMinerM33V10,
        "10": BTMinerM33V10,
        "20": BTMinerM33V20,
        "30": BTMinerM33V30,
    },
    "M33S": {
        "Default": BTMinerM33SVG30,
        "BTMiner": BTMinerM33SVG30,
        "G30": BTMinerM33SVG30,
    },
    "M33S+": {
        "Default": BTMinerM33SPlusVH20,
        "BTMiner": BTMinerM33SPlusVH20,
        "H20": BTMinerM33SPlusVH20,
        "H30": BTMinerM33SPlusVH30,
    },
    "M33S++": {
        "Default": BTMinerM33SPlusPlusVH20,
        "BTMiner": BTMinerM33SPlusPlusVH20,
        "H20": BTMinerM33SPlusPlusVH20,
        "H30": BTMinerM33SPlusPlusVH30,
        "G40": BTMinerM33SPlusPlusVG40,
    },
    "M34S+": {
        "Default": BTMinerM34SPlusVE10,
        "BTMiner": BTMinerM34SPlusVE10,
        "E10": BTMinerM34SPlusVE10,
    },
    "M36S": {
        "Default": BTMinerM36SVE10,
        "BTMiner": BTMinerM36SVE10,
        "E10": BTMinerM36SVE10,
    },
    "M36S+": {
        "Default": BTMinerM36SPlusVG30,
        "BTMiner": BTMinerM36SPlusVG30,
        "G30": BTMinerM36SPlusVG30,
    },
    "M36S++": {
        "Default": BTMinerM36SPlusPlusVH30,
        "BTMiner": BTMinerM36SPlusPlusVH30,
        "H30": BTMinerM36SPlusPlusVH30,
    },
    "M39": {"Default": BTMinerM39V20, "BTMiner": BTMinerM39V20, "20": BTMinerM39V20},
    "M50": {
        "Default": BTMinerM50VG30,
        "BTMiner": BTMinerM50VG30,
        "G30": BTMinerM50VG30,
        "H10": BTMinerM50VH10,
        "H20": BTMinerM50VH20,
        "H30": BTMinerM50VH30,
        "H40": BTMinerM50VH40,
        "H50": BTMinerM50VH50,
        "H60": BTMinerM50VH60,
        "H70": BTMinerM50VH70,
        "H80": BTMinerM50VH80,
        "J10": BTMinerM50VJ10,
        "J20": BTMinerM50VJ20,
        "J30": BTMinerM50VJ30,
    },
    "M50S": {
        "Default": BTMinerM50SVJ10,
        "BTMiner": BTMinerM50SVJ10,
        "J10": BTMinerM50SVJ10,
        "J20": BTMinerM50SVJ20,
        "J30": BTMinerM50SVJ30,
        "H10": BTMinerM50SVH10,
        "H20": BTMinerM50SVH20,
        "H30": BTMinerM50SVH30,
        "H40": BTMinerM50SVH40,
        "H50": BTMinerM50SVH50,
    },
    "M50S+": {
        "Default": BTMinerM50SPlusVH30,
        "BTMiner": BTMinerM50SPlusVH30,
        "H30": BTMinerM50SPlusVH30,
        "H40": BTMinerM50SPlusVH40,
        "J30": BTMinerM50SPlusVJ30,
    },
    "M50S++": {
        "Default": BTMinerM50SPlusPlusVK10,
        "BTMiner": BTMinerM50SPlusPlusVK10,
        "K10": BTMinerM50SPlusPlusVK10,
        "K20": BTMinerM50SPlusPlusVK20,
        "K30": BTMinerM50SPlusPlusVK30,
    },
    "M53": {
        "Default": BTMinerM53VH30,
        "BTMiner": BTMinerM53VH30,
        "H30": BTMinerM53VH30,
    },
    "M53S": {
        "Default": BTMinerM53SVH30,
        "BTMiner": BTMinerM53SVH30,
        "H30": BTMinerM53SVH30,
    },
    "M53S+": {
        "Default": BTMinerM53SPlusVJ30,
        "BTMiner": BTMinerM53SPlusVJ30,
        "J30": BTMinerM53SPlusVJ30,
    },
    "M56": {
        "Default": BTMinerM56VH30,
        "BTMiner": BTMinerM56VH30,
        "H30": BTMinerM56VH30,
    },
    "M56S": {
        "Default": BTMinerM56SVH30,
        "BTMiner": BTMinerM56SVH30,
        "H30": BTMinerM56SVH30,
    },
    "M56S+": {
        "Default": BTMinerM56SPlusVJ30,
        "BTMiner": BTMinerM56SPlusVJ30,
        "J30": BTMinerM56SPlusVJ30,
    },
    "M59": {
        "Default": BTMinerM59VH30,
        "BTMiner": BTMinerM59VH30,
        "H30": BTMinerM59VH30,
    },
    "AVALONMINER 721": {
        "Default": CGMinerAvalon721,
        "CGMiner": CGMinerAvalon721,
    },
    "AVALONMINER 741": {
        "Default": CGMinerAvalon741,
        "CGMiner": CGMinerAvalon741,
    },
    "AVALONMINER 761": {
        "Default": CGMinerAvalon761,
        "CGMiner": CGMinerAvalon761,
    },
    "AVALONMINER 821": {
        "Default": CGMinerAvalon821,
        "CGMiner": CGMinerAvalon821,
    },
    "AVALONMINER 841": {
        "Default": CGMinerAvalon841,
        "CGMiner": CGMinerAvalon841,
    },
    "AVALONMINER 851": {
        "Default": CGMinerAvalon851,
        "CGMiner": CGMinerAvalon851,
    },
    "AVALONMINER 921": {
        "Default": CGMinerAvalon921,
        "CGMiner": CGMinerAvalon921,
    },
    "AVALONMINER 1026": {
        "Default": CGMinerAvalon1026,
        "CGMiner": CGMinerAvalon1026,
    },
    "AVALONMINER 1047": {
        "Default": CGMinerAvalon1047,
        "CGMiner": CGMinerAvalon1047,
    },
    "AVALONMINER 1066": {
        "Default": CGMinerAvalon1066,
        "CGMiner": CGMinerAvalon1066,
    },
    "T3H+": {
        "Default": CGMinerInnosiliconT3HPlus,
        "CGMiner": CGMinerInnosiliconT3HPlus,
    },
    "A10X": {
        "Default": CGMinerA10X,
        "CGMiner": CGMinerA10X,
    },
    "Unknown": {"Default": UnknownMiner},
}


# TODO: Implement caching and cache clearing.
# TODO: Add Canaan support back
# TODO: Improve consistency
class MinerFactory:
    async def web_ping(self, ip: str):
        tasks = [self._http_ping(ip), self._http_ping(ip, https=True)]
        d = asyncio.as_completed(
            tasks,
            timeout=TIMEOUT,
        )
        for i in d:
            try:
                data = await i
                if data[0] is not None:
                    if not "400 - Bad Request" in data[0]:
                        return data
            except asyncio.TimeoutError:
                pass
        return None, False

    async def _http_ping(
        self, ip: str, https: bool = False
    ) -> Tuple[Optional[str], bool]:
        request = "GET / HTTP/1.1\r\nHost: pyasic\r\n\r\n"
        if https:
            request = "GET / HTTPS/1.1\r\nHost: pyasic\r\n\r\n"
        try:
            reader, writer = await asyncio.open_connection(str(ip), 80)
            response = None
            try:
                writer.write(request.encode())
                response = await reader.read()
            except asyncio.CancelledError:
                writer.close()
                await writer.wait_closed()
                if response is not None:
                    data = response.decode()
                    if data is not None and not data == "":
                        return data, True
            else:
                writer.close()
                await writer.wait_closed()
                data = response.decode()
                if data is not None and not data == "":
                    return data, True
        except OSError:
            pass
        return None, False

    async def sock_ping(self, ip: str) -> [Optional[dict], bool]:
        try:
            data = await self.send_api_command(ip, "devdetails")
            if data:
                return data, True
        except (asyncio.exceptions.TimeoutError, OSError, ConnectionError):
            pass
        return None, False

    async def get_miner(self, ip: str):
        try:
            return await asyncio.wait_for(self._get_miner(ip), TIMEOUT)
        except asyncio.TimeoutError:
            return None

    async def _get_miner(self, ip: str):
        sock_data = None
        web_data = None
        for i in range(LOOPS):
            web_result, sock_result = await asyncio.gather(
                self.web_ping(ip), self.sock_ping(ip)
            )
            online = sock_result[1] or web_result[1]
            if online:
                web_data = web_result[0]
                sock_data = sock_result[0]
                break

        if web_data:
            if "401 Unauthorized" and 'realm="antMiner' in web_data:
                # antminer branch
                return await self.get_miner_antminer(ip)
            if "307 Temporary Redirect" and 'location="https://' in web_data:
                return await self.get_miner_whatsminer(ip)
            if "Braiins OS" in web_data:
                return "BOS+"
            if "cloud-box" in web_data:
                # goldshell branch
                return await self.get_miner_goldshell(ip)

        if sock_data:
            if "bitmicro" in str(sock_data):
                return await self.get_miner_whatsminer(ip, sock_data)
            if "intchains_qomo" in str(sock_data):
                return await self.get_miner_goldshell(ip)
            return UnknownMiner(ip)

    async def send_web_command(
        self,
        ip: Union[ipaddress.ip_address, str],
        location: str,
        auth: Optional[httpx.DigestAuth] = None,
    ) -> Optional[dict]:
        async with httpx.AsyncClient(verify=False, timeout=TIMEOUT) as client:
            try:
                data = await client.get(
                    f"http://{str(ip)}{location}",
                    auth=auth,
                    timeout=TIMEOUT,
                )
            except httpx.HTTPError:
                logger.info(f"{ip}: Web command timeout.")
                return
        if data is None:
            return
        try:
            json_data = data.json()
        except json.JSONDecodeError:
            return
        else:
            return json_data

    async def send_api_command(
        self, ip: Union[ipaddress.ip_address, str], command: str
    ) -> Optional[dict]:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(str(ip), 4028), timeout=TIMEOUT
            )
        except (ConnectionError, OSError):
            return
        cmd = {"command": command}

        # send the command
        writer.write(json.dumps(cmd).encode("utf-8"))
        await writer.drain()

        # instantiate data
        data = b""

        # loop to receive all the data
        while True:
            d = await reader.read(4096)
            if not d:
                break
            data += d

        writer.close()
        await writer.wait_closed()

        data = await self.fix_api_data(data)

        data = json.loads(data)

        return data

    async def fix_api_data(self, data: bytes):
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
        str_data = str_data.replace("info", "1nfo")
        str_data = str_data.replace("inf", "0")
        str_data = str_data.replace("1nfo", "info")
        str_data = str_data.replace("nan", "0")
        # fix whatever this garbage from avalonminers is `,"id":1}`
        if str_data.startswith(","):
            str_data = f"{{{str_data[1:]}"
        # try to fix an error with overflowing the recieve buffer
        # this can happen in cases such as bugged btminers returning arbitrary length error info with 100s of errors.
        if not str_data.endswith("}"):
            str_data = ",".join(str_data.split(",")[:-1]) + "}"

        # fix a really nasty bug with whatsminer API v2.0.4 where they return a list structured like a dict
        if re.search(r"\"error_code\":\[\".+\"\]", str_data):
            str_data = str_data.replace("[", "{").replace("]", "}")

        return str_data

    async def get_miner_antminer(self, ip: str):
        sock_json_data = await self.send_api_command(ip, "version")
        try:
            miner_type = sock_json_data["VERSION"][0]["Type"]
            api_type = None
            api_ver = sock_json_data["VERSION"][0]["API"]
            keys_str = "_".join(sock_json_data["VERSION"][0].keys())
            if "cgminer" in keys_str:
                api_type = "CGMiner"
            elif "bmminer" in keys_str:
                api_type = "BMMiner"
            return self._select_miner_from_classes(
                ip=IPv4Address(ip),
                model=miner_type.upper(),
                api=api_type,
                ver=None,
                api_ver=api_ver,
            )
        except (TypeError, LookupError):
            pass

        # last resort, this is slow
        auth = httpx.DigestAuth("root", "root")
        web_json_data = await self.send_web_command(
            ip, "/cgi-bin/get_system_info.cgi", auth=auth
        )

        if not web_json_data:
            return UnknownMiner(ip)

        if web_json_data.get("minertype") is not None:
            miner_type = web_json_data["minertype"].upper()
            api_type = None
            if "cgminer" in "_".join(web_json_data.keys()):
                api_type = "CGMiner"
            elif "bmminer" in "_".join(web_json_data.keys()):
                api_type = "BMMiner"
            return self._select_miner_from_classes(
                IPv4Address(ip), miner_type, api_type, None
            )

    async def get_miner_goldshell(self, ip: str):
        json_data = await self.send_web_command(ip, "/mcb/status")

        if json_data.get("model") is not None:
            miner_type = json_data["model"].replace("-", " ").upper()
            return self._select_miner_from_classes(
                IPv4Address(ip), miner_type, None, None
            )

    async def get_miner_whatsminer(self, ip: str, json_data: Optional[dict] = None):
        if not json_data:
            try:
                json_data = await self.send_api_command(ip, "devdetails")
            except (asyncio.exceptions.TimeoutError, OSError, ConnectionError):
                return None

        try:
            miner_type, submodel = json_data["DEVDETAILS"][0]["Model"].split("V")
            return self._select_miner_from_classes(
                IPv4Address(ip), miner_type, submodel, None
            )
        except LookupError:
            return None

    @staticmethod
    def _select_miner_from_classes(
        ip: ipaddress.ip_address,
        model: Union[str, None],
        api: Union[str, None],
        ver: Union[str, None],
        api_ver: Union[str, None] = None,
    ) -> AnyMiner:
        miner = UnknownMiner(str(ip))
        # make sure we have model information
        if model:
            if not api:
                api = "Default"

            if model not in MINER_CLASSES.keys():
                if "avalon" in model:
                    if model == "avalon10":
                        miner = CGMinerAvalon1066(str(ip), api_ver)
                    else:
                        miner = CGMinerAvalon821(str(ip), api_ver)
                return miner
            if api not in MINER_CLASSES[model].keys():
                api = "Default"
            if ver in MINER_CLASSES[model].keys():
                miner = MINER_CLASSES[model][ver](str(ip), api_ver)
                return miner
            miner = MINER_CLASSES[model][api](str(ip), api_ver)

        # if we cant find a model, check if we found the API
        else:

            # return the miner base class with some API if we found it
            if api:
                if "BOSMiner+" in api:
                    miner = BOSMiner(str(ip), api_ver)
                elif "BOSMiner" in api:
                    miner = BOSMinerOld(str(ip), api_ver)
                elif "CGMiner" in api:
                    miner = CGMiner(str(ip), api_ver)
                elif "BTMiner" in api:
                    miner = BTMiner(str(ip), api_ver)
                elif "BMMiner" in api:
                    miner = BMMiner(str(ip), api_ver)

        return miner


FACTORY = MinerFactory()
