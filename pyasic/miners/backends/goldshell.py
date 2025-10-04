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

from typing import Any

from pydantic import BaseModel, Field, ValidationError

from pyasic.config import MinerConfig
from pyasic.config.mining import MiningModeConfig
from pyasic.data.boards import HashBoard
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


class GoldshellPoolInfo(BaseModel):
    url: str = ""
    user: str = ""
    pass_: str = Field("", alias="pass")
    dragid: int = 0

    class Config:
        extra = "allow"
        populate_by_name = True


class GoldshellPoolsWrapper(BaseModel):
    pools: list[GoldshellPoolInfo]

    class Config:
        extra = "allow"


class GoldshellPowerPlan(BaseModel):
    level: str | None = None

    class Config:
        extra = "allow"


class GoldshellSettings(BaseModel):
    name: str = ""
    firmware: str = ""
    powerplans: list[GoldshellPowerPlan] = []
    select: int = 0

    class Config:
        extra = "allow"


class GoldshellDevInfo(BaseModel):
    ID: int | None = None
    MHS_20s: float = Field(0, alias="MHS 20s")
    tstemp_2: float = Field(0, alias="tstemp-2")
    chips_nr: int = Field(0, alias="chips-nr")

    class Config:
        extra = "allow"
        populate_by_name = True


class GoldshellDevsWrapper(BaseModel):
    DEVS: list[GoldshellDevInfo] | None = None

    class Config:
        extra = "allow"


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
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
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
            if self.config is not None:
                return self.config
            return MinerConfig()

        try:
            if isinstance(pools, dict):
                pools_wrapper = GoldshellPoolsWrapper.model_validate(pools)
                pools_list = [
                    pool.model_dump(by_alias=True) for pool in pools_wrapper.pools
                ]
            else:
                pools_list = pools
            self.config = MinerConfig.from_goldshell_list(pools_list)
        except ValidationError as e:
            logger.warning(f"{self} - Failed to parse pools config: {e}")
            self.config = MinerConfig()
        return self.config

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        pools_data = await self.web.pools()
        # have to delete all the pools one at a time first
        try:
            if isinstance(pools_data, dict):
                pools_wrapper = GoldshellPoolsWrapper.model_validate(pools_data)
                pools_list = pools_wrapper.pools
            else:
                pools_list = []
                for pool in pools_data:
                    try:
                        pool_info = GoldshellPoolInfo.model_validate(pool)
                        pools_list.append(pool_info)
                    except ValidationError as e:
                        logger.warning(f"{self} - Failed to parse pool info: {e}")
                        continue

            for pool in pools_list:
                await self.web.delpool(
                    url=pool.url,
                    user=pool.user,
                    password=pool.pass_,
                    dragid=pool.dragid,
                )
        except ValidationError as e:
            logger.warning(f"{self} - Failed to parse pools for deletion: {e}")

        self.config = config
        cfg = config.as_goldshell(user_suffix=user_suffix)
        # send them back 1 at a time
        for pool in cfg["pools"]:
            pool_info = GoldshellPoolInfo.model_validate(pool)
            await self.web.newpool(
                url=pool_info.url, user=pool_info.user, password=pool_info.pass_
            )

        settings_data = await self.web.setting()
        settings = GoldshellSettings.model_validate(settings_data)
        cfg_level = cfg.get("settings", {}).get("level")
        for idx, plan in enumerate(settings.powerplans):
            if plan.level == cfg_level:
                settings.select = idx
                break
        await self.web.set_setting(settings.model_dump())

    async def _get_mac(self, web_setting: dict[str, Any] | None = None) -> str | None:
        if web_setting is None:
            try:
                web_setting = await self.web.setting()
            except APIError:
                return None

        if web_setting is not None:
            try:
                settings = GoldshellSettings.model_validate(web_setting)
                return settings.name if settings.name else None
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse settings for MAC: {e}")
        return None

    async def _get_fw_ver(self, web_status: dict[str, Any] | None = None) -> str | None:
        if web_status is None:
            try:
                web_status = await self.web.setting()
            except APIError:
                return None

        if web_status is not None:
            try:
                settings = GoldshellSettings.model_validate(web_status)
                return settings.firmware if settings.firmware else None
            except ValidationError as e:
                logger.warning(
                    f"{self} - Failed to parse settings for firmware version: {e}"
                )
        return None

    async def _get_hashboards(
        self,
        rpc_devs: dict[str, Any] | None = None,
        rpc_devdetails: dict[str, Any] | None = None,
    ) -> list[HashBoard]:
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
            try:
                devs_wrapper = GoldshellDevsWrapper.model_validate(rpc_devs)
                if devs_wrapper.DEVS:
                    for board in devs_wrapper.DEVS:
                        if board.ID is not None:
                            hashboards[board.ID].hashrate = self.algo.hashrate(
                                rate=board.MHS_20s,
                                unit=self.algo.unit.MH,  # type: ignore[attr-defined]
                            ).into(
                                self.algo.unit.default  # type: ignore[attr-defined]
                            )
                            hashboards[board.ID].temp = round(board.tstemp_2)
                            hashboards[board.ID].missing = False
                else:
                    logger.error(f"{self} - No DEVS data found in response")
            except ValidationError as e:
                logger.error(f"{self} - Failed to parse devs: {e}")

        if rpc_devdetails is None:
            try:
                rpc_devdetails = await self.rpc.devdetails()
            except APIError:
                pass

        if rpc_devdetails is not None:
            try:
                devdetails_wrapper = GoldshellDevsWrapper.model_validate(rpc_devdetails)
                if devdetails_wrapper.DEVS:
                    for board in devdetails_wrapper.DEVS:
                        if board.ID is not None:
                            hashboards[board.ID].chips = board.chips_nr
                else:
                    logger.error(f"{self} - No DEVS data found in devdetails response")
            except ValidationError as e:
                logger.error(f"{self} - Failed to parse devdetails: {e}")

        return hashboards

    async def stop_mining(self) -> bool:
        settings_data = await self.web.setting()
        settings = GoldshellSettings.model_validate(settings_data)
        mode = MiningModeConfig.sleep()
        cfg = mode.as_goldshell()
        level = cfg.get("settings", {}).get("level")
        for idx, plan in enumerate(settings.powerplans):
            if plan.level == level:
                settings.select = idx
                break
        await self.web.set_setting(settings.model_dump())
        return True

    async def resume_mining(self) -> bool:
        settings_data = await self.web.setting()
        settings = GoldshellSettings.model_validate(settings_data)
        mode = MiningModeConfig.normal()
        cfg = mode.as_goldshell()
        level = cfg.get("settings", {}).get("level")
        for idx, plan in enumerate(settings.powerplans):
            if plan.level == level:
                settings.select = idx
                break
        await self.web.set_setting(settings.model_dump())
        return True
