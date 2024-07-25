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

import re
from typing import List, Optional

from pyasic.data import AlgoHashRate, Fan, HashBoard, HashUnit
from pyasic.errors import APIError
from pyasic.miners.backends.cgminer import CGMiner
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, RPCAPICommand

AVALON_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [RPCAPICommand("rpc_version", "version")],
        ),
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
            [RPCAPICommand("rpc_devs", "devs")],
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
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
    }
)


class AvalonMiner(CGMiner):
    """Handler for Avalon Miners"""

    data_locations = AVALON_DATA_LOC

    async def fault_light_on(self) -> bool:
        try:
            data = await self.rpc.ascset(0, "led", "1-1")
        except APIError:
            return False
        if data["STATUS"][0]["Msg"] == "ASC 0 set OK":
            return True
        return False

    async def fault_light_off(self) -> bool:
        try:
            data = await self.rpc.ascset(0, "led", "1-0")
        except APIError:
            return False
        if data["STATUS"][0]["Msg"] == "ASC 0 set OK":
            return True
        return False

    async def reboot(self) -> bool:
        try:
            data = await self.rpc.restart()
        except APIError:
            return False

        try:
            if data["STATUS"] == "RESTART":
                return True
        except KeyError:
            return False
        return False

    @staticmethod
    def parse_stats(stats):
        _stats_items = re.findall(".+?\\[*?]", stats)
        stats_items = []
        stats_dict = {}
        for item in _stats_items:
            if ":" in item:
                data = item.replace("]", "").split("[")
                data_list = [i.split(": ") for i in data[1].strip().split(", ")]
                data_dict = {}
                try:
                    for key, val in [tuple(item) for item in data_list]:
                        data_dict[key] = val
                except ValueError:
                    # --avalon args
                    for arg_item in data_list:
                        item_data = arg_item[0].split(" ")
                        for idx, val in enumerate(item_data):
                            if idx % 2 == 0 or idx == 0:
                                data_dict[val] = item_data[idx + 1]

                raw_data = [data[0].strip(), data_dict]
            else:
                raw_data = [
                    value
                    for value in item.replace("[", " ")
                    .replace("]", " ")
                    .split(" ")[:-1]
                    if value != ""
                ]
                if len(raw_data) == 1:
                    raw_data.append("")
            if raw_data[0] == "":
                raw_data = raw_data[1:]

            if len(raw_data) == 2:
                stats_dict[raw_data[0]] = raw_data[1]
            else:
                stats_dict[raw_data[0]] = raw_data[1:]
            stats_items.append(raw_data)

        return stats_dict

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(self, rpc_version: dict = None) -> Optional[str]:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                pass

        if rpc_version is not None:
            try:
                base_mac = rpc_version["VERSION"][0]["MAC"]
                base_mac = base_mac.upper()
                mac = ":".join(
                    [base_mac[i : (i + 2)] for i in range(0, len(base_mac), 2)]
                )
                return mac
            except (KeyError, ValueError):
                pass

    async def _get_hashrate(self, rpc_devs: dict = None) -> Optional[AlgoHashRate]:
        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                pass

        if rpc_devs is not None:
            try:
                return AlgoHashRate.SHA256(
                    rpc_devs["DEVS"][0]["MHS 1m"], HashUnit.SHA256.MH
                ).into(self.algo.unit.default)
            except (KeyError, IndexError, ValueError, TypeError):
                pass

    async def _get_hashboards(self, rpc_stats: dict = None) -> List[HashBoard]:
        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                unparsed_stats = rpc_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
            except (IndexError, KeyError, ValueError, TypeError):
                return hashboards

            for board in range(self.expected_hashboards):
                try:
                    hashboards[board].chip_temp = int(parsed_stats["MTmax"][board])
                except LookupError:
                    pass

                try:
                    board_hr = parsed_stats["MGHS"][board]
                    hashboards[board].hashrate = AlgoHashRate.SHA256(
                        board_hr, HashUnit.SHA256.GH
                    ).into(self.algo.unit.default)
                except LookupError:
                    pass

                try:
                    hashboards[board].temp = int(parsed_stats["MTavg"][board])
                except LookupError:
                    pass

                try:
                    chip_data = parsed_stats[f"PVT_T{board}"]
                    hashboards[board].missing = False
                    if chip_data:
                        hashboards[board].chips = len(
                            [item for item in chip_data if not item == "0"]
                        )
                except LookupError:
                    pass

        return hashboards

    async def _get_expected_hashrate(
        self, rpc_stats: dict = None
    ) -> Optional[AlgoHashRate]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                unparsed_stats = rpc_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
                return AlgoHashRate.SHA256(
                    parsed_stats["GHSmm"], HashUnit.SHA256.GH
                ).into(self.algo.unit.default)
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def _get_env_temp(self, rpc_stats: dict = None) -> Optional[float]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                unparsed_stats = rpc_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
                return float(parsed_stats["Temp"])
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def _get_wattage_limit(self, rpc_stats: dict = None) -> Optional[int]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                unparsed_stats = rpc_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
                return int(parsed_stats["MPO"])
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def _get_fans(self, rpc_stats: dict = None) -> List[Fan]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        fans_data = [Fan() for _ in range(self.expected_fans)]
        if rpc_stats is not None:
            try:
                unparsed_stats = rpc_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
            except LookupError:
                return fans_data

            for fan in range(self.expected_fans):
                try:
                    fans_data[fan].speed = int(parsed_stats[f"Fan{fan + 1}"])
                except (IndexError, KeyError, ValueError, TypeError):
                    pass
        return fans_data

    async def _get_fault_light(self, rpc_stats: dict = None) -> Optional[bool]:
        if self.light:
            return self.light
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                unparsed_stats = rpc_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
                led = int(parsed_stats["Led"])
                return True if led == 1 else False
            except (IndexError, KeyError, ValueError, TypeError):
                pass

        try:
            data = await self.rpc.ascset(0, "led", "1-255")
        except APIError:
            return False
        try:
            if data["STATUS"][0]["Msg"] == "ASC 0 set info: LED[1]":
                return True
        except LookupError:
            pass
        return False
