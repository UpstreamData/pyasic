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
from typing import List

from pyasic.config import MinerConfig, MiningModeConfig
from pyasic.data import AlgoHashRate, HashBoard, HashUnit
from pyasic.errors import APIError
from pyasic.logger import logger
from pyasic.miners.backends import BFGMiner
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.web.goldshell import GoldshellWebAPI

GOLDSHELL_DATA_LOC = DataLocations(
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
            [RPCAPICommand("rpc_stats", "stats")],
        ),
    }
)


class GoldshellMiner(BFGMiner):
    """Handler for goldshell miners"""

    _web_cls = GoldshellWebAPI
    web: GoldshellWebAPI

    data_locations = GOLDSHELL_DATA_LOC

    supports_shutdown = True
    supports_power_modes = True

    async def get_config(self) -> MinerConfig:
        # get pool data
        try:
            pools = await self.web.pools()
        except APIError:
            return self.config

        self.config = MinerConfig.from_goldshell(pools)
        return self.config

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
        cfg = config.as_goldshell(user_suffix=user_suffix)
        # send them back 1 at a time
        for pool in cfg["pools"]:
            await self.web.newpool(
                url=pool["url"], user=pool["user"], password=pool["pass"]
            )

        settings = await self.web.setting()
        for idx, plan in enumerate(settings["powerplans"]):
            if plan["level"] == cfg["settings"]["level"]:
                settings["select"] = idx
        await self.web.set_setting(settings)

    async def _get_mac(self, web_setting: dict = None) -> str:
        if web_setting is None:
            try:
                web_setting = await self.web.setting()
            except APIError:
                pass

        if web_setting is not None:
            try:
                return web_setting["name"]
            except KeyError:
                pass

    async def _get_fw_ver(self, web_status: dict = None) -> str:
        if web_status is None:
            try:
                web_status = await self.web.setting()
            except APIError:
                pass

        if web_status is not None:
            try:
                return web_status["firmware"]
            except KeyError:
                pass

    async def _get_hashboards(
        self, rpc_devs: dict = None, rpc_devdetails: dict = None
    ) -> List[HashBoard]:
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
                            hashboards[b_id].hashrate = AlgoHashRate.SHA256(
                                board["MHS 20s"], HashUnit.SHA256.MH
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
                    if board.get("ID") is not None:
                        try:
                            b_id = board["ID"]
                            hashboards[b_id].chips = board["chips-nr"]
                        except KeyError:
                            pass
            else:
                logger.error(self, rpc_devdetails)

        return hashboards

    async def stop_mining(self) -> bool:
        settings = await self.web.setting()
        mode = MiningModeConfig.sleep()
        cfg = mode.as_goldshell()
        level = cfg["settings"]["level"]
        for idx, plan in enumerate(settings["powerplans"]):
            if plan["level"] == level:
                settings["select"] = idx
        await self.web.set_setting(settings)
        return True

    async def resume_mining(self) -> bool:
        settings = await self.web.setting()
        mode = MiningModeConfig.normal()
        cfg = mode.as_goldshell()
        level = cfg["settings"]["level"]
        for idx, plan in enumerate(settings["powerplans"]):
            if plan["level"] == level:
                settings["select"] = idx
        await self.web.set_setting(settings)
        return True
