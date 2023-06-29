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

from typing import List, Optional

import asyncssh

from pyasic.data import HashBoard
from pyasic.errors import APIError
from pyasic.miners.backends import Hiveon
from pyasic.miners.types import T9


class HiveonT9(Hiveon, T9):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        self.ip = ip
        self.pwd = "admin"

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(self):
        try:
            mac = (
                (await self.send_ssh_command("cat /sys/class/net/eth0/address"))
                .strip()
                .upper()
            )
            return mac
        except (TypeError, ValueError, asyncssh.Error, OSError, AttributeError):
            pass

    async def get_hashboards(self, api_stats: dict = None) -> List[HashBoard]:
        board_map = {
            0: [2, 9, 10],
            1: [3, 11, 12],
            2: [4, 13, 14],
        }
        hashboards = []

        for board in board_map:
            hashboard = HashBoard(slot=board, expected_chips=self.nominal_chips)
            hashrate = 0
            chips = 0
            for chipset in board_map[board]:
                if hashboard.chip_temp == None:
                    try:
                        hashboard.board_temp = api_stats["STATS"][1][f"temp{chipset}"]
                        hashboard.chip_temp = api_stats["STATS"][1][f"temp2_{chipset}"]
                    except (KeyError, IndexError):
                        pass
                    else:
                        hashboard.missing = False
                try:
                    hashrate += api_stats["STATS"][1][f"chain_rate{chipset}"]
                    chips += api_stats["STATS"][1][f"chain_acn{chipset}"]
                except (KeyError, IndexError):
                    pass
            hashboard.hashrate = round(hashrate / 1000, 2)
            hashboard.chips = chips
            hashboards.append(hashboard)

        return hashboards

    async def get_wattage(self, api_stats: dict = None) -> Optional[int]:
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            boards = api_stats.get("STATS")
            try:
                wattage_raw = boards[1]["chain_power"]
            except (KeyError, IndexError):
                pass
            else:
                # parse wattage position out of raw data
                return round(float(wattage_raw.split(" ")[0]))

    async def get_env_temp(self, api_stats: dict = None) -> Optional[float]:
        env_temp_list = []
        board_map = {
            0: [2, 9, 10],
            1: [3, 11, 12],
            2: [4, 13, 14],
        }
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass
        if api_stats:
            for board in board_map.values():
                for chipset in board:
                    try:
                        env_temp = api_stats["STATS"][1][f"temp3_{chipset}"]
                        if not env_temp == 0:
                            env_temp_list.append(int(env_temp))
                    except (KeyError, IndexError):
                        pass

            if not env_temp_list == []:
                return round(float(sum(env_temp_list) / len(env_temp_list)), 2)
