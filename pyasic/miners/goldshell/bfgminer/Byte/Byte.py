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
from pyasic.data import Fan, MinerData
from pyasic.data.boards import HashBoard
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.errors import APIError
from pyasic.logger import logger
from pyasic.miners.backends import GoldshellMiner
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.miners.device.models import Byte

ALGORITHM_SCRYPT_NAME = "scrypt(LTC)"
EXPECTED_CHIPS_PER_SCRYPT_BOARD = 5

GOLDSHELL_BYTE_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_setting", "setting")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_status", "status")],
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
            [
                RPCAPICommand("rpc_devs", "devs"),
                RPCAPICommand("rpc_devdetails", "devdetails"),
            ],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_devs", "devs")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
    }
)

class GoldshellByte(GoldshellMiner, Byte):

    data_locations = GOLDSHELL_BYTE_DATA_LOC

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
            except APIError:
                pass

        scrypt_board_count = 0
        total_wattage = 0
        total_uptime_mins = 0

        for minfo in self.cgdev.get("minfos", []):

            for info in minfo.get("infos", []):
                
                self.expected_hashboards += 1

                total_wattage = float(info.get("power", 0))
                total_uptime_mins = int(info.get("time", 0))

                if minfo.get("name") == ALGORITHM_SCRYPT_NAME:
                    scrypt_board_count += 1

        data = await super().get_data(allow_warning, include, exclude)

        data.expected_chips = (EXPECTED_CHIPS_PER_SCRYPT_BOARD * scrypt_board_count)
        data.expected_fans = scrypt_board_count
        data.wattage = total_wattage
        data.uptime = total_uptime_mins
        data.voltage = 0

        for board in data.hashboards:
            data.voltage += board.voltage

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
                            hashboards[b_id].chip_temp = board["tstemp-1"]
                            hashboards[b_id].temp = board["tstemp-2"]
                            hashboards[b_id].voltage = board["voltage"]
                            hashboards[b_id].missing = False

                            if board.get("pool") == ALGORITHM_SCRYPT_NAME:
                                hashboards[b_id].expected_chips = EXPECTED_CHIPS_PER_SCRYPT_BOARD

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
    
    async def _get_fans(self, rpc_devs: dict = None) -> List[Fan]:
        if self.expected_fans is None:
            return []

        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                pass

        fans_data = []

        if rpc_devs is not None:
            if rpc_devs.get("DEVS"):
                for board in rpc_devs["DEVS"]:
                    if board.get("PGA") is not None:
                        try:
                            b_id = board["PGA"]
                            fan_speed = board[f"fan{b_id}"]
                            fans_data.append(fan_speed)

                        except KeyError:
                            pass
            else:
                logger.error(self, rpc_devs)

        fans = [Fan(speed=d) if d else Fan() for d in fans_data]

        return fans