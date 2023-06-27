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

import logging
import re
from typing import List, Optional

from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard
from pyasic.data.error_codes import MinerErrorData
from pyasic.errors import APIError
from pyasic.miners.backends import CGMiner

AVALON_DATA_LOC = {
    "mac": {"cmd": "get_mac", "kwargs": {"api_version": {"api": "version"}}},
    "model": {"cmd": "get_model", "kwargs": {}},
    "api_ver": {"cmd": "get_api_ver", "kwargs": {"api_version": {"api": "version"}}},
    "fw_ver": {"cmd": "get_fw_ver", "kwargs": {"api_version": {"api": "version"}}},
    "hostname": {"cmd": "get_hostname", "kwargs": {"mac": {"api": "version"}}},
    "hashrate": {"cmd": "get_hashrate", "kwargs": {"api_devs": {"api": "devs"}}},
    "nominal_hashrate": {
        "cmd": "get_nominal_hashrate",
        "kwargs": {"api_stats": {"api": "stats"}},
    },
    "hashboards": {"cmd": "get_hashboards", "kwargs": {"api_stats": {"api": "stats"}}},
    "env_temp": {"cmd": "get_env_temp", "kwargs": {"api_stats": {"api": "stats"}}},
    "wattage": {"cmd": "get_wattage", "kwargs": {}},
    "wattage_limit": {
        "cmd": "get_wattage_limit",
        "kwargs": {"api_stats": {"api": "stats"}},
    },
    "fans": {"cmd": "get_fans", "kwargs": {"api_stats": {"api": "stats"}}},
    "fan_psu": {"cmd": "get_fan_psu", "kwargs": {}},
    "errors": {"cmd": "get_errors", "kwargs": {}},
    "fault_light": {
        "cmd": "get_fault_light",
        "kwargs": {"api_stats": {"api": "stats"}},
    },
    "pools": {"cmd": "get_pools", "kwargs": {"api_pools": {"api": "pools"}}},
    "is_mining": {"cmd": "is_mining", "kwargs": {}},
    "uptime": {"cmd": "get_uptime", "kwargs": {}},
}


class CGMinerAvalon(CGMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver)

        # data gathering locations
        self.data_locations = AVALON_DATA_LOC

    async def fault_light_on(self) -> bool:
        try:
            data = await self.api.ascset(0, "led", "1-1")
        except APIError:
            return False
        if data["STATUS"][0]["Msg"] == "ASC 0 set OK":
            return True
        return False

    async def fault_light_off(self) -> bool:
        try:
            data = await self.api.ascset(0, "led", "1-0")
        except APIError:
            return False
        if data["STATUS"][0]["Msg"] == "ASC 0 set OK":
            return True
        return False

    async def reboot(self) -> bool:
        try:
            data = await self.api.restart()
        except APIError:
            return False

        try:
            if data["STATUS"] == "RESTART":
                return True
        except KeyError:
            return False
        return False

    async def stop_mining(self) -> bool:
        return False

    async def resume_mining(self) -> bool:
        return False

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        """Configures miner with yaml config."""
        self.config = config
        return None
        logging.debug(f"{self}: Sending config.")  # noqa - This doesnt work...
        conf = config.as_avalon(user_suffix=user_suffix)
        try:
            data = await self.api.ascset(  # noqa
                0, "setpool", f"root,root,{conf}"
            )  # this should work but doesn't
        except APIError:
            pass
        # return data

    @staticmethod
    def parse_stats(stats):
        _stats_items = re.findall(".+?\[*?]", stats)
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
                        for idx in range(len(item_data)):
                            if idx % 2 == 0 or idx == 0:
                                data_dict[item_data[idx]] = item_data[idx + 1]

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

    async def get_mac(self, api_version: dict = None) -> Optional[str]:
        if not api_version:
            try:
                api_version = await self.api.version()
            except APIError:
                pass

        if api_version:
            try:
                base_mac = api_version["VERSION"][0]["MAC"]
                base_mac = base_mac.upper()
                mac = ":".join(
                    [base_mac[i : (i + 2)] for i in range(0, len(base_mac), 2)]
                )
                return mac
            except (KeyError, ValueError):
                pass

    async def get_hostname(self, mac: str = None) -> Optional[str]:
        if not mac:
            mac = await self.get_mac()

        if mac:
            return f"Avalon{mac.replace(':', '')[-6:]}"

    async def get_hashrate(self, api_devs: dict = None) -> Optional[float]:
        if not api_devs:
            try:
                api_devs = await self.api.devs()
            except APIError:
                pass

        if api_devs:
            try:
                return round(float(api_devs["DEVS"][0]["MHS 1m"] / 1000000), 2)
            except (KeyError, IndexError, ValueError, TypeError):
                pass

    async def get_hashboards(self, api_stats: dict = None) -> List[HashBoard]:
        hashboards = [
            HashBoard(slot=i, expected_chips=self.nominal_chips)
            for i in range(self.ideal_hashboards)
        ]

        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            try:
                unparsed_stats = api_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
            except (IndexError, KeyError, ValueError, TypeError):
                return hashboards

            for board in range(self.ideal_hashboards):
                try:
                    hashboards[board].chip_temp = int(parsed_stats["MTmax"][board])
                except LookupError:
                    pass

                try:
                    board_hr = parsed_stats["MGHS"][board]
                    hashboards[board].hashrate = round(float(board_hr) / 1000, 2)
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

    async def get_nominal_hashrate(self, api_stats: dict = None) -> Optional[float]:
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            try:
                unparsed_stats = api_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
                return round(float(parsed_stats["GHSmm"]) / 1000, 2)
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def get_env_temp(self, api_stats: dict = None) -> Optional[float]:
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            try:
                unparsed_stats = api_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
                return float(parsed_stats["Temp"])
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def get_wattage(self) -> Optional[int]:
        return None

    async def get_wattage_limit(self, api_stats: dict = None) -> Optional[int]:
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            try:
                unparsed_stats = api_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
                return int(parsed_stats["MPO"])
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def get_fans(self, api_stats: dict = None) -> List[Fan]:
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        fans_data = [Fan() for _ in range(self.fan_count)]
        if api_stats:
            try:
                unparsed_stats = api_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
            except LookupError:
                return fans_data

            for fan in range(self.fan_count):
                try:
                    fans_data[fan].speed = int(parsed_stats[f"Fan{fan + 1}"])
                except (IndexError, KeyError, ValueError, TypeError):
                    pass
        return fans_data

    async def get_pools(self, api_pools: dict = None) -> List[dict]:
        groups = []

        if not api_pools:
            try:
                api_pools = await self.api.pools()
            except APIError:
                pass

        if api_pools:
            try:
                pools = {}
                for i, pool in enumerate(api_pools["POOLS"]):
                    pools[f"pool_{i + 1}_url"] = (
                        pool["URL"]
                        .replace("stratum+tcp://", "")
                        .replace("stratum2+tcp://", "")
                    )
                    pools[f"pool_{i + 1}_user"] = pool["User"]
                    pools["quota"] = pool["Quota"] if pool.get("Quota") else "0"

                groups.append(pools)
            except KeyError:
                pass
        return groups

    async def get_errors(self) -> List[MinerErrorData]:
        return []

    async def get_fault_light(self, api_stats: dict = None) -> bool:  # noqa
        if self.light:
            return self.light
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            try:
                unparsed_stats = api_stats["STATS"][0]["MM ID0"]
                parsed_stats = self.parse_stats(unparsed_stats)
                led = int(parsed_stats["Led"])
                return True if led == 1 else False
            except (IndexError, KeyError, ValueError, TypeError):
                pass

        try:
            data = await self.api.ascset(0, "led", "1-255")
        except APIError:
            return False
        try:
            if data["STATUS"][0]["Msg"] == "ASC 0 set info: LED[1]":
                return True
        except LookupError:
            pass
        return False

    async def is_mining(self, *args, **kwargs) -> Optional[bool]:
        return None
