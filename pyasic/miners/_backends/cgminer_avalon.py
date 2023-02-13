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

import ipaddress
import logging
import re
from collections import namedtuple
from typing import List, Optional, Tuple, Union

from pyasic.API.cgminer import CGMinerAPI
from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard, MinerData
from pyasic.data.error_codes import MinerErrorData
from pyasic.errors import APIError
from pyasic.miners._backends import CGMiner
from pyasic.miners.base import BaseMiner
from pyasic.settings import PyasicSettings


class CGMinerAvalon(CGMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver)
        self.ip = ip

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
        return None
        logging.debug(f"{self}: Sending config.")  # noqa - This doesnt work...
        conf = config.as_avalon(user_suffix=user_suffix)
        try:
            data = await self.api.ascset(
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
                for key, val in [tuple(item) for item in data_list]:
                    data_dict[key] = val
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

    async def get_hashrate(self, api_summary: dict = None) -> Optional[float]:
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return round(float(api_summary["SUMMARY"][0]["MHS 1m"] / 1000000), 2)
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
                stats_data = api_stats[0].get("STATS")
                if stats_data:
                    for key in stats_data[0].keys():
                        if key.startswith("MM ID"):
                            raw_data = self.parse_stats(stats_data[0][key])
                            for board in range(self.ideal_hashboards):
                                chip_temp = raw_data.get("MTmax")
                                if chip_temp:
                                    hashboards[board].chip_temp = chip_temp[board]

                                temp = raw_data.get("MTavg")
                                if temp:
                                    hashboards[board].temp = temp[board]

                                chips = raw_data.get(f"PVT_T{board}")
                                if chips:
                                    hashboards[board].chips = len(
                                        [item for item in chips if not item == "0"]
                                    )
            except (IndexError, KeyError, ValueError, TypeError):
                pass

        return hashboards

    async def get_env_temp(self) -> Optional[float]:
        return None

    async def get_wattage(self) -> Optional[int]:
        return None

    async def get_wattage_limit(self) -> Optional[int]:
        return None

    async def get_fans(self, api_stats: dict = None) -> List[Fan]:
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        fans_data = [Fan(), Fan(), Fan(), Fan()]
        if api_stats:
            try:
                stats_data = api_stats[0].get("STATS")
                if stats_data:
                    for key in stats_data[0].keys():
                        if key.startswith("MM ID"):
                            raw_data = self.parse_stats(stats_data[0][key])
                            for fan in range(self.fan_count):
                                fans_data[fan] = Fan(int(raw_data[f"Fan{fan + 1}"]))
            except (KeyError, IndexError, ValueError, TypeError):
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

    async def get_fault_light(self) -> bool:
        if self.light:
            return self.light
        try:
            data = await self.api.ascset(0, "led", "1-255")
        except APIError:
            return False
        if data["STATUS"][0]["Msg"] == "ASC 0 set info: LED[1]":
            return True
        return False
