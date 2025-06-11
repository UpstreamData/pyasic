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
from typing import List, Union
from pyasic.config import MinerConfig
from pyasic.data import MinerData
from pyasic.data.boards import HashBoard
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.errors import APIError
from pyasic.logger import logger
from pyasic.miners.backends import GoldshellMiner
from pyasic.miners.data import DataOptions
from pyasic.miners.device.models import Byte


class GoldshellByte(GoldshellMiner, Byte):

    cgdev: dict | None = None

    async def get_data(
        self,
        allow_warning: bool = False,
        include: List[Union[str, DataOptions]] = None,
        exclude: List[Union[str, DataOptions]] = None,
    ) -> MinerData:
        if self.cgdev is None:
            try:
                self.cgdev = await self.web.send_command("cgminer?cgminercmd=devs")
                print(self.cgdev)

                for minfo in self.cgdev.get("minfos", []):
                    for _ in minfo.get("infos", []):
                        self.expected_hashboards += 1
            except APIError:
                pass

        data = await super().get_data(allow_warning, include, exclude)

        return data
    
    async def get_config(self) -> MinerConfig:
        # get pool data
        try:
            pools = await self.web.pools()
        except APIError:
            return self.config

        self.config = MinerConfig.from_goldshell_byte(pools)
        return self.config
    
    async def _get_pools(self, rpc_pools: dict = None) -> List[PoolMetrics]:
        if rpc_pools is None:
            try:
                rpc_pools = await self.rpc.pools()
            except APIError:
                pass

        pools_data = []
        if rpc_pools is not None:
            try:
                pools = rpc_pools.get("POOLS", [])
                for index, pool_info in enumerate(pools):
                    url = pool_info.get("URL")
                    pool_url = PoolUrl.from_str(url) if url else None
                    pool_data = PoolMetrics(
                        accepted=pool_info.get("Accepted"),
                        rejected=pool_info.get("Rejected"),
                        active=pool_info.get("Stratum Active"),
                        alive=pool_info.get("Status") == "Alive",
                        url=pool_url,
                        user=pool_info.get("User"),
                        index=index,
                    )
                    pools_data.append(pool_data)
            except LookupError:
                pass
        return pools_data
    
    async def _get_hashboards(
        self, rpc_devs: dict = None, rpc_devdetails: dict = None
    ) -> List[HashBoard]:
        if self.expected_hashboards is None:
            return []

        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                pass

        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if rpc_devs is not None:
            if rpc_devs.get("DEVS"):
                for board in rpc_devs["DEVS"]:
                    if board.get("PGA") is not None:
                        try:
                            b_id = board["PGA"]
                            hashboards[b_id].hashrate = self.algo.hashrate(
                                rate=float(board["MHS 20s"]), unit=self.algo.unit.MH
                            ).into(self.algo.unit.default)
                            hashboards[b_id].temp = board["tstemp-2"]
                            hashboards[b_id].missing = False
                        except KeyError:
                            pass
            else:
                logger.error(self, rpc_devs)

        if rpc_devdetails is None:
            try:
                rpc_devdetails = await self.rpc.devdetails()
            except APIError:
                pass

        if rpc_devdetails is not None:
            if rpc_devdetails.get("DEVS"):
                for board in rpc_devdetails["DEVS"]:
                    if board.get("DEVDETAILS") is not None:
                        try:
                            b_id = board["DEVDETAILS"]
                            hashboards[b_id].chips = board["chips-nr"]
                        except KeyError:
                            pass
            else:
                logger.error(self, rpc_devdetails)

        return hashboards