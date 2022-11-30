#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import ipaddress

from pyasic.miners._backends import BMMiner


class Hiveon(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api_type = "Hiveon"
        self.uname = "root"
        self.pwd = "admin"

    async def get_board_info(self) -> dict:
        """Gets data on each board and chain in the miner."""
        board_stats = await self.api.stats()
        stats = board_stats["STATS"][1]
        boards = {}
        board_chains = {0: [2, 9, 10], 1: [3, 11, 12], 2: [4, 13, 14]}
        for idx, board in enumerate(board_chains):
            boards[board] = []
            for chain in board_chains[board]:
                count = stats[f"chain_acn{chain}"]
                chips = stats[f"chain_acs{chain}"].replace(" ", "")
                if not count == 18 or "x" in chips:
                    nominal = False
                else:
                    nominal = True
                boards[board].append(
                    {
                        "chain": chain,
                        "chip_count": count,
                        "chip_status": chips,
                        "nominal": nominal,
                    }
                )
        return boards

    async def get_bad_boards(self) -> dict:
        """Checks for and provides list of non working boards."""
        boards = await self.get_board_info()
        bad_boards = {}
        for board in boards.keys():
            for chain in boards[board]:
                if not chain["chip_count"] == 18 or "x" in chain["chip_status"]:
                    if board not in bad_boards.keys():
                        bad_boards[board] = []
                    bad_boards[board].append(chain)
        return bad_boards

    async def set_power_limit(self, wattage: int) -> bool:
        return False
