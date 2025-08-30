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
import copy
import re
import time
from typing import List, Optional

from pyasic.data import Fan, HashBoard
from pyasic.device.algorithm import AlgoHashRate
from pyasic.errors import APIError
from pyasic.miners.backends.cgminer import CGMiner
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, RPCAPICommand
from pyasic.rpc.avalonminer import AvalonMinerRPCAPI

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
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction(
            "_get_env_temp",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
    }
)


class AvalonMiner(CGMiner):
    """Handler for Avalon Miners"""

    _rpc_cls = AvalonMinerRPCAPI
    rpc: AvalonMinerRPCAPI

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

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            if wattage < 3:
                limit = wattage
            elif wattage > 100:
                limit = 2
            elif wattage > 80:
                limit = 1
            else:
                limit = 0
            data = await self.rpc.ascset(0, "worklevel,set", 1)
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

    async def stop_mining(self) -> bool:
        try:
            # Shut off 5 seconds from now
            timestamp = int(time.time()) + 5
            data = await self.rpc.ascset(0, f"softoff", f"1:{timestamp}")
        except APIError:
            return False
        if "success" in data["STATUS"][0]["Msg"]:
            return True
        return False

    async def resume_mining(self) -> bool:
        try:
            # Shut off 5 seconds from now
            timestamp = int(time.time()) + 5
            data = await self.rpc.ascset(0, f"softon", f"1:{timestamp}")
        except APIError:
            return False
        if "success" in data["STATUS"][0]["Msg"]:
            return True
        return False

    @staticmethod
    def parse_estats(data):
        # Deep copy to preserve original structure
        new_data = copy.deepcopy(data)

        def convert_value(val, key):
            val = val.strip()

            if key == "SYSTEMSTATU":
                return val

            if " " in val:
                parts = val.split()
                result = []
                for part in parts:
                    if part.isdigit():
                        result.append(int(part))
                    else:
                        try:
                            result.append(float(part))
                        except ValueError:
                            result.append(part)
                return result
            else:
                if val.isdigit():
                    return int(val)
                try:
                    return float(val)
                except ValueError:
                    return val

        def parse_info_block(info_str):
            pattern = re.compile(r"(\w+)\[([^\]]*)\]")
            return {
                key: convert_value(val, key) for key, val in pattern.findall(info_str)
            }

        for stat in new_data.get("STATS", []):
            keys_to_replace = {}

            for key, value in stat.items():
                if "MM" in key:
                    # Normalize key by removing suffix after colon
                    norm_key = key.split(":")[0]

                    mm_data = value
                    if not isinstance(mm_data, str):
                        continue
                    if mm_data.startswith("'STATS':"):
                        mm_data = mm_data[len("'STATS':") :]
                    keys_to_replace[norm_key] = parse_info_block(mm_data)

                elif key == "HBinfo":
                    match = re.search(r"'(\w+)':\{(.+)\}", value)
                    if match:
                        hb_key = match.group(1)
                        hb_data = match.group(2)
                        keys_to_replace[key] = {hb_key: parse_info_block(hb_data)}

            # Remove old keys and insert parsed versions
            for k in list(stat.keys()):
                if "MM" in k or k == "HBinfo":
                    del stat[k]
            stat.update(keys_to_replace)

        return new_data

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
                return self.algo.hashrate(
                    rate=float(rpc_devs["DEVS"][0]["MHS 1m"]), unit=self.algo.unit.MH
                ).into(self.algo.unit.default)
            except (KeyError, IndexError, ValueError, TypeError):
                pass

    async def _get_hashboards(self, rpc_estats: dict = None) -> List[HashBoard]:
        if self.expected_hashboards is None:
            return []

        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if rpc_estats is None:
            try:
                rpc_estats = await self.rpc.estats()
            except APIError:
                pass

        if rpc_estats is not None:
            try:
                parsed_estats = self.parse_estats(rpc_estats)
            except (IndexError, KeyError, ValueError, TypeError):
                return hashboards

            for board in range(self.expected_hashboards):
                try:
                    board_hr = parsed_estats["STATS"][0]["MM ID0"]["MGHS"]
                    if isinstance(board_hr, list):
                        hashboards[board].hashrate = self.algo.hashrate(
                            rate=float(board_hr[board]), unit=self.algo.unit.GH
                        ).into(self.algo.unit.default)
                    else:
                        hashboards[board].hashrate = self.algo.hashrate(
                            rate=float(board_hr), unit=self.algo.unit.GH
                        ).into(self.algo.unit.default)

                except LookupError:
                    pass

                try:
                    hashboards[board].chip_temp = int(
                        parsed_estats["STATS"][0]["MM ID0"]["MTmax"][board]
                    )
                except (LookupError, TypeError):
                    try:
                        hashboards[board].chip_temp = int(
                            parsed_estats["STATS"][0]["MM ID0"].get("Tmax", parsed_estats["STATS"][0]["MM ID0"]["TMax"])
                        )
                    except LookupError:
                        pass

                try:
                    hashboards[board].temp = int(
                        parsed_estats["STATS"][0]["MM ID0"]["MTmax"][board]
                    )
                except (LookupError, TypeError):
                    try:
                        hashboards[board].temp = int(
                            parsed_estats["STATS"][0]["MM ID0"].get("Tavg", parsed_estats["STATS"][0]["MM ID0"]["TAvg"])
                        )
                    except LookupError:
                        pass

                try:
                    hashboards[board].inlet_temp = int(
                        parsed_estats["STATS"][0]["MM ID0"]["MTavg"][board]
                    )
                except (LookupError, TypeError):
                    try:
                        hashboards[board].inlet_temp = int(
                            parsed_estats["STATS"][0]["MM ID0"]["HBITemp"]
                        )
                    except LookupError:
                        pass

                try:
                    hashboards[board].outlet_temp = int(
                        parsed_estats["STATS"][0]["MM ID0"]["MTmax"][board]
                    )
                except (LookupError, TypeError):
                    try:
                        hashboards[board].outlet_temp = int(
                            parsed_estats["STATS"][0]["MM ID0"]["HBOTemp"]
                        )
                    except LookupError:
                        pass

                try:
                    chip_data = parsed_estats["STATS"][0]["MM ID0"][f"PVT_T{board}"]
                    hashboards[board].missing = False
                    if chip_data:
                        hashboards[board].chips = len(
                            [item for item in chip_data if not item == "0"]
                        )
                except (LookupError, TypeError):
                    try:
                        chip_data = parsed_estats["STATS"][0]["HBinfo"][f"HB{board}"][
                            f"PVT_T{board}"
                        ]
                        hashboards[board].missing = False
                        if chip_data:
                            hashboards[board].chips = len(
                                [item for item in chip_data if not item == "0"]
                            )
                    except LookupError:
                        pass

        return hashboards

    async def _get_expected_hashrate(
        self, rpc_estats: dict = None
    ) -> Optional[AlgoHashRate]:
        if rpc_estats is None:
            try:
                rpc_estats = await self.rpc.estats()
            except APIError:
                pass

        if rpc_estats is not None:
            try:
                parsed_estats = self.parse_estats(rpc_estats)["STATS"][0]["MM ID0"]
                return self.algo.hashrate(
                    rate=float(parsed_estats["GHSmm"]), unit=self.algo.unit.GH
                ).into(self.algo.unit.default)
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def _get_env_temp(self, rpc_estats: dict = None) -> Optional[float]:
        if rpc_estats is None:
            try:
                rpc_estats = await self.rpc.estats()
            except APIError:
                pass

        if rpc_estats is not None:
            try:
                parsed_estats = self.parse_estats(rpc_estats)["STATS"][0]["MM ID0"]
                return float(parsed_estats["Temp"])
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def _get_wattage_limit(self, rpc_estats: dict = None) -> Optional[int]:
        if rpc_estats is None:
            try:
                rpc_estats = await self.rpc.estats()
            except APIError:
                pass

        if rpc_estats is not None:
            try:
                parsed_estats = self.parse_estats(rpc_estats)["STATS"][0]["MM ID0"]
                return int(parsed_estats["MPO"])
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def _get_wattage(self, rpc_estats: dict = None) -> Optional[int]:
        if rpc_estats is None:
            try:
                rpc_estats = await self.rpc.estats()
            except APIError:
                pass

        if rpc_estats is not None:
            try:
                parsed_estats = self.parse_estats(rpc_estats)["STATS"][0]["MM ID0"]
                return int(parsed_estats["WALLPOWER"])
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def _get_fans(self, rpc_estats: dict = None) -> List[Fan]:
        if self.expected_fans is None:
            return []

        if rpc_estats is None:
            try:
                rpc_estats = await self.rpc.estats()
            except APIError:
                pass

        fans_data = [Fan() for _ in range(self.expected_fans)]
        if rpc_estats is not None:
            try:
                parsed_estats = self.parse_estats(rpc_estats)["STATS"][0]["MM ID0"]
            except LookupError:
                return fans_data

            for fan in range(self.expected_fans):
                try:
                    fans_data[fan].speed = int(parsed_estats[f"Fan{fan + 1}"])
                except (IndexError, KeyError, ValueError, TypeError):
                    pass
        return fans_data

    async def _get_fault_light(self, rpc_estats: dict = None) -> Optional[bool]:
        if self.light:
            return self.light
        if rpc_estats is None:
            try:
                rpc_estats = await self.rpc.estats()
            except APIError:
                pass

        if rpc_estats is not None:
            try:
                parsed_estats = self.parse_estats(rpc_estats)["STATS"][0]["MM ID0"]
                led = int(parsed_estats["Led"])
                return True if led == 1 else False
            except (IndexError, KeyError, ValueError, TypeError):
                pass
        return False
