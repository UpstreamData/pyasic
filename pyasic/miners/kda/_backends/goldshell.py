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
from pyasic.data import Fan, HashBoard
from pyasic.errors import APIError
from pyasic.miners.hns._backends import BFGMiner
from pyasic.web.goldshell import GoldshellWebAPI


class Goldshell(BFGMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver)
        self.web = GoldshellWebAPI(ip)

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

    async def get_hashboards(self, api_devs: dict = None) -> List[HashBoard]:
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
            for board in api_devs["DEVS"]:
                if board.get("ID"):
                    try:
                        b_id = board["ID"]
                        hashboards[b_id].hashrate = round(board["MHS 20s"] / 1000000, 2)
                        hashboards[b_id].temp = board["tstemp-2"]
                        hashboards[b_id].missing = False
                    except KeyError:
                        pass

        return hashboards
