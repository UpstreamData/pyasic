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

from pyasic.data import AlgoHashRate, HashBoard, HashUnit
from pyasic.errors import APIError
from pyasic.miners.backends import Hiveon
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, RPCAPICommand
from pyasic.miners.device.models import T9

HIVEON_T9_DATA_LOC = DataLocations(
    **{
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction(
            "_get_env_temp",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
    }
)


class HiveonT9(Hiveon, T9):
    data_locations = HIVEON_T9_DATA_LOC

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

    async def _get_hashboards(self, rpc_stats: dict = None) -> List[HashBoard]:
        hashboards = [
            HashBoard(slot=board, expected_chips=self.expected_chips)
            for board in range(self.expected_hashboards)
        ]

        if rpc_stats is None:
            try:
                rpc_stats = self.rpc.stats()
            except APIError:
                return []

        board_map = {
            0: [2, 9, 10],
            1: [3, 11, 12],
            2: [4, 13, 14],
        }

        for board in board_map:
            hashrate = 0
            chips = 0
            for chipset in board_map[board]:
                if hashboards[board].chip_temp is None:
                    try:
                        hashboards[board].temp = rpc_stats["STATS"][1][f"temp{chipset}"]
                        hashboards[board].chip_temp = rpc_stats["STATS"][1][
                            f"temp2_{chipset}"
                        ]
                    except (KeyError, IndexError):
                        pass
                    else:
                        hashboards[board].missing = False
                try:
                    hashrate += rpc_stats["STATS"][1][f"chain_rate{chipset}"]
                    chips += rpc_stats["STATS"][1][f"chain_acn{chipset}"]
                except (KeyError, IndexError):
                    pass
            hashboards[board].hashrate = AlgoHashRate.SHA256(
                hashrate, HashUnit.SHA256.GH
            ).into(self.algo.unit.default)
            hashboards[board].chips = chips

        return hashboards

    async def _get_wattage(self, rpc_stats: dict = None) -> Optional[int]:
        if not rpc_stats:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats:
            boards = rpc_stats.get("STATS")
            try:
                wattage_raw = boards[1]["chain_power"]
            except (KeyError, IndexError):
                pass
            else:
                # parse wattage position out of raw data
                return round(float(wattage_raw.split(" ")[0]))

    async def _get_env_temp(self, rpc_stats: dict = None) -> Optional[float]:
        env_temp_list = []
        board_map = {
            0: [2, 9, 10],
            1: [3, 11, 12],
            2: [4, 13, 14],
        }
        if not rpc_stats:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass
        if rpc_stats:
            for board in board_map.values():
                for chipset in board:
                    try:
                        env_temp = rpc_stats["STATS"][1][f"temp3_{chipset}"]
                        if not env_temp == 0:
                            env_temp_list.append(int(env_temp))
                    except (KeyError, IndexError):
                        pass

            if not env_temp_list == []:
                return round(float(sum(env_temp_list) / len(env_temp_list)), 2)
