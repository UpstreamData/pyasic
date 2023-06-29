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

from pyasic.config import MinerConfig
from pyasic.data import HashBoard
from pyasic.errors import APIError
from pyasic.logger import logger
from pyasic.miners.backends import BFGMiner
from pyasic.web.goldshell import GoldshellWebAPI

GOLDSHELL_DATA_LOC = {
    "mac": {"cmd": "get_mac", "kwargs": {"web_setting": {"web": "setting"}}},
    "model": {"cmd": "get_model", "kwargs": {}},
    "api_ver": {"cmd": "get_api_ver", "kwargs": {"api_version": {"api": "version"}}},
    "fw_ver": {"cmd": "get_fw_ver", "kwargs": {"web_status": {"web": "status"}}},
    "hostname": {"cmd": "get_hostname", "kwargs": {}},
    "hashrate": {"cmd": "get_hashrate", "kwargs": {"api_summary": {"api": "summary"}}},
    "nominal_hashrate": {
        "cmd": "get_nominal_hashrate",
        "kwargs": {"api_stats": {"api": "stats"}},
    },
    "hashboards": {
        "cmd": "get_hashboards",
        "kwargs": {
            "api_devs": {"api": "devs"},
            "api_devdetails": {"api": "devdetails"},
        },
    },
    "env_temp": {"cmd": "get_env_temp", "kwargs": {}},
    "wattage": {"cmd": "get_wattage", "kwargs": {}},
    "wattage_limit": {"cmd": "get_wattage_limit", "kwargs": {}},
    "fans": {"cmd": "get_fans", "kwargs": {"api_stats": {"api": "stats"}}},
    "fan_psu": {"cmd": "get_fan_psu", "kwargs": {}},
    "errors": {"cmd": "get_errors", "kwargs": {}},
    "fault_light": {"cmd": "get_fault_light", "kwargs": {}},
    "pools": {"cmd": "get_pools", "kwargs": {"api_pools": {"api": "pools"}}},
    "is_mining": {"cmd": "is_mining", "kwargs": {}},
    "uptime": {"cmd": "get_uptime", "kwargs": {}},
}


class BFGMinerGoldshell(BFGMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver)
        # interfaces
        self.web = GoldshellWebAPI(ip)

        # static data
        # data gathering locations
        self.data_locations = GOLDSHELL_DATA_LOC

    async def get_config(self) -> MinerConfig:
        return MinerConfig().from_raw(await self.web.pools())

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        pools_data = await self.web.pools()
        # have to delete all the pools one at a time first
        for pool in pools_data:
            await self.web.delpool(
                url=pool["url"],
                user=pool["user"],
                password=pool["pass"],
                dragid=pool["dragid"],
            )

        self.config = config

        # send them back 1 at a time
        for pool in config.as_goldshell(user_suffix=user_suffix):
            await self.web.newpool(
                url=pool["url"], user=pool["user"], password=pool["pass"]
            )

    async def get_mac(self, web_setting: dict = None) -> str:
        if not web_setting:
            try:
                web_setting = await self.web.setting()
            except APIError:
                pass

        if web_setting:
            try:
                return web_setting["name"]
            except KeyError:
                pass

    async def get_fw_ver(self, web_status: dict = None) -> str:
        if not web_status:
            try:
                web_status = await self.web.setting()
            except APIError:
                pass

        if web_status:
            try:
                return web_status["firmware"]
            except KeyError:
                pass

    async def get_hashboards(
        self, api_devs: dict = None, api_devdetails: dict = None
    ) -> List[HashBoard]:
        if not api_devs:
            try:
                api_devs = await self.api.devs()
            except APIError:
                pass

        hashboards = [
            HashBoard(slot=i, expected_chips=self.nominal_chips)
            for i in range(self.ideal_hashboards)
        ]

        if api_devs:
            if api_devs.get("DEVS"):
                for board in api_devs["DEVS"]:
                    if board.get("ID") is not None:
                        try:
                            b_id = board["ID"]
                            hashboards[b_id].hashrate = round(
                                board["MHS 20s"] / 1000000, 2
                            )
                            hashboards[b_id].temp = board["tstemp-2"]
                            hashboards[b_id].missing = False
                        except KeyError:
                            pass
            else:
                logger.error(self, api_devs)

        if not api_devdetails:
            try:
                api_devdetails = await self.api.devdetails()
            except APIError:
                pass

        if api_devdetails:
            if api_devdetails.get("DEVS"):
                for board in api_devdetails["DEVS"]:
                    if board.get("ID") is not None:
                        try:
                            b_id = board["ID"]
                            hashboards[b_id].chips = board["chips-nr"]
                        except KeyError:
                            pass
            else:
                logger.error(self, api_devdetails)

        return hashboards

    async def is_mining(self, *args, **kwargs) -> Optional[bool]:
        return None

    async def get_uptime(self, *args, **kwargs) -> Optional[int]:
        return None
