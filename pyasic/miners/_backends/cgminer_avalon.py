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
import logging
from typing import List, Union, Tuple, Optional
from collections import namedtuple
import re

from pyasic.API.cgminer import CGMinerAPI
from pyasic.config import MinerConfig
from pyasic.data import HashBoard, MinerData
from pyasic.data.error_codes import MinerErrorData
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner
from pyasic.settings import PyasicSettings
from pyasic.miners._backends import CGMiner


class CGMinerAvalon(CGMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver)
        self.ip = ip

    async def fault_light_on(self) -> bool:
        data = await self.api.ascset(0, "led", "1-1")
        if data["STATUS"][0]["Msg"] == "ASC 0 set OK":
            return True
        return False

    async def fault_light_off(self) -> bool:
        data = await self.api.ascset(0, "led", "1-0")
        if data["STATUS"][0]["Msg"] == "ASC 0 set OK":
            return True
        return False

    async def reboot(self) -> bool:
        if (await self.api.restart())["STATUS"] == "RESTART":
            return True
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
        data = await self.api.ascset(
            0, "setpool", f"root,root,{conf}"
        )  # this should work but doesn't
        return data

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
            api_summary = await self.api.summary()

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

    async def get_fans(
        self, api_stats: dict = None
    ) -> Tuple[
        Tuple[Optional[int], Optional[int], Optional[int], Optional[int]],
        Tuple[Optional[int]],
    ]:
        fan_speeds = namedtuple("FanSpeeds", "fan_1 fan_2 fan_3 fan_4")
        psu_fan_speeds = namedtuple("PSUFanSpeeds", "psu_fan")
        miner_fan_speeds = namedtuple("MinerFans", "fan_speeds psu_fan_speeds")

        psu_fans = psu_fan_speeds(None)

        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        fans_data = [None, None, None, None]
        if api_stats:
            try:
                stats_data = api_stats[0].get("STATS")
                if stats_data:
                    for key in stats_data[0].keys():
                        if key.startswith("MM ID"):
                            raw_data = self.parse_stats(stats_data[0][key])
                            for fan in range(self.fan_count):
                                fans_data[fan] = int(raw_data[f"Fan{fan + 1}"])
            except (KeyError, IndexError, ValueError, TypeError):
                pass
        fans = fan_speeds(*fans_data)

        return miner_fan_speeds(fans, psu_fans)

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
        data = await self.api.ascset(0, "led", "1-255")
        if data["STATUS"][0]["Msg"] == "ASC 0 set info: LED[1]":
            return True
        return False

    async def _get_data(self, allow_warning: bool) -> dict:
        miner_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            try:
                miner_data = await self.api.multicommand(
                    "summary",
                    "pools",
                    "version",
                    "devdetails",
                    "stats",
                    allow_warning=allow_warning,
                )
            except APIError:
                pass
            if miner_data:
                break
        if miner_data:
            summary = miner_data.get("summary")
            if summary:
                summary = summary[0]
            pools = miner_data.get("pools")
            if pools:
                pools = pools[0]
            version = miner_data.get("version")
            if version:
                version = version[0]
            devdetails = miner_data.get("devdetails")
            if devdetails:
                devdetails = devdetails[0]
            stats = miner_data.get("stats")
            if stats:
                stats = stats[0]
        else:
            summary, pools, devdetails, version, stats = (None for _ in range(5))

        data = {  # noqa - Ignore dictionary could be re-written
            # ip - Done at start
            # datetime - Done auto
            "mac": await self.get_mac(),
            "model": await self.get_model(api_devdetails=devdetails),
            # make - Done at start
            # api_ver - Done at end
            # fw_ver - Done at end
            "hostname": await self.get_hostname(),
            "hashrate": await self.get_hashrate(api_summary=summary),
            "hashboards": await self.get_hashboards(api_stats=stats),
            # ideal_hashboards - Done at start
            "env_temp": await self.get_env_temp(),
            "wattage": await self.get_wattage(),
            "wattage_limit": await self.get_wattage_limit(),
            # fan_1 - Done at end
            # fan_2 - Done at end
            # fan_3 - Done at end
            # fan_4 - Done at end
            # fan_psu - Done at end
            # ideal_chips - Done at start
            # pool_split - Done at end
            # pool_1_url - Done at end
            # pool_1_user - Done at end
            # pool_2_url - Done at end
            # pool_2_user - Done at end
            "errors": await self.get_errors(),
            "fault_light": await self.get_fault_light(),
        }

        data["api_ver"], data["fw_ver"] = await self.get_version(api_version=version)
        fan_data = await self.get_fans()

        data["fan_1"] = fan_data.fan_speeds.fan_1  # noqa
        data["fan_2"] = fan_data.fan_speeds.fan_2  # noqa
        data["fan_3"] = fan_data.fan_speeds.fan_3  # noqa
        data["fan_4"] = fan_data.fan_speeds.fan_4  # noqa

        data["fan_psu"] = fan_data.psu_fan_speeds.psu_fan  # noqa

        pools_data = await self.get_pools(api_pools=pools)
        data["pool_1_url"] = pools_data[0]["pool_1_url"]
        data["pool_1_user"] = pools_data[0]["pool_1_user"]
        if len(pools_data) > 1:
            data["pool_2_url"] = pools_data[1]["pool_1_url"]
            data["pool_2_user"] = pools_data[1]["pool_1_user"]
            data["pool_split"] = f"{pools_data[0]['quota']}/{pools_data[1]['quota']}"
        else:
            try:
                data["pool_2_url"] = pools_data[0]["pool_1_url"]
                data["pool_2_user"] = pools_data[0]["pool_1_user"]
                data["quota"] = "0"
            except KeyError:
                pass

        return data
