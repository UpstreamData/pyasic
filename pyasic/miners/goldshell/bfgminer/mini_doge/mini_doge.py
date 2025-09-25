# ------------------------------------------------------------------------------
#  Copyright 2025 Upstream Data Inc                                            -
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

from pyasic.config import MinerConfig
from pyasic.data.boards import HashBoard
from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
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
from pyasic.miners.device.models import MiniDoge

GOLDSHELL_MINI_DOGE_DATA_LOC = DataLocations(
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
            [RPCAPICommand("rpc_devs", "devs")],
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
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [WebAPICommand("web_devs", "devs")],
        ),
    }
)


class GoldshellMiniDoge(GoldshellMiner, MiniDoge):
    data_locations = GOLDSHELL_MINI_DOGE_DATA_LOC
    supports_shutdown = False
    supports_power_modes = False

    async def get_config(self) -> MinerConfig | None:  # type: ignore[override]
        try:
            pools = await self.web.pools()
        except APIError:
            if self.config is not None:
                return self.config

        self.config = MinerConfig.from_goldshell(pools)
        return self.config

    async def _get_expected_hashrate(
        self, rpc_devs: dict | None = None
    ) -> AlgoHashRateType | None:
        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                pass

        if rpc_devs is not None:
            try:
                hash_rate = rpc_devs["DEVS"][0]["estimate_hash_rate"]
                return self.algo.hashrate(
                    rate=float(hash_rate), unit=self.algo.unit.H
                ).into(self.algo.unit.default)
            except KeyError:
                pass

        return None

    async def _get_hashboards(
        self, rpc_devs: dict | None = None, rpc_devdetails: dict | None = None
    ) -> list[HashBoard]:
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
                    if board.get("ID") is not None:
                        try:
                            b_id = board["ID"]
                            hashboards[b_id].hashrate = self.algo.hashrate(
                                rate=float(board["MHS 20s"]), unit=self.algo.unit.MH
                            ).into(self.algo.unit.default)
                            hashboards[b_id].chip_temp = board["tstemp-0"]
                            hashboards[b_id].temp = board["tstemp-1"]
                            hashboards[b_id].voltage = board["voltage"]
                            hashboards[b_id].active = board["Status"] == "Alive"
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
                    if board.get("ID") is not None:
                        try:
                            b_id = board["ID"]
                            hashboards[b_id].chips = board["chips-nr"]
                        except KeyError:
                            pass
            else:
                logger.error(self, rpc_devdetails)

        return hashboards

    async def _get_uptime(self, web_devs: dict | None = None) -> int | None:
        if web_devs is None:
            try:
                web_devs = await self.web.devs()
            except APIError:
                pass

        if web_devs is not None:
            try:
                uptime = int(web_devs["data"][0]["time"])
                return uptime
            except KeyError:
                pass

        return None
