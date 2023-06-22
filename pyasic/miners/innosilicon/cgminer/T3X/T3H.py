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
from typing import List, Optional

from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard
from pyasic.data.error_codes import InnosiliconError, MinerErrorData
from pyasic.errors import APIError
from pyasic.miners.backends import CGMiner
from pyasic.miners.types import T3HPlus
from pyasic.web.inno import InnosiliconWebAPI


class CGMinerT3HPlus(CGMiner, T3HPlus):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        self.ip = ip
        self.web = InnosiliconWebAPI(ip)

    async def fault_light_on(self) -> bool:
        return False

    async def fault_light_off(self) -> bool:
        return False

    async def get_config(self, api_pools: dict = None) -> MinerConfig:
        if not api_pools:
            try:
                api_pools = await self.api.pools()
            except APIError as e:
                logging.warning(e)

        if api_pools:
            if "POOLS" in api_pools.keys():
                cfg = MinerConfig().from_api(api_pools["POOLS"])
                self.config = cfg
        return self.config

    async def reboot(self) -> bool:
        try:
            data = await self.web.reboot()
        except APIError:
            pass
        else:
            return data["success"]

    async def restart_cgminer(self) -> bool:
        try:
            data = await self.web.restart_cgminer()
        except APIError:
            pass
        else:
            return data["success"]

    async def restart_backend(self) -> bool:
        return await self.restart_cgminer()

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config
        await self.web.update_pools(config.as_inno(user_suffix=user_suffix))

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(
        self, web_get_all: dict = None, web_overview: dict = None
    ) -> Optional[str]:
        if web_get_all:
            web_get_all = web_get_all["all"]

        if not web_get_all and not web_overview:
            try:
                web_overview = await self.web.overview()
            except APIError:
                pass

        if web_get_all:
            try:
                mac = web_get_all["mac"]
                return mac.upper()
            except KeyError:
                pass

        if web_overview:
            try:
                mac = web_overview["version"]["ethaddr"]
                return mac.upper()
            except KeyError:
                pass

    async def get_hashrate(
        self, api_summary: dict = None, web_get_all: dict = None
    ) -> Optional[float]:
        if web_get_all:
            web_get_all = web_get_all["all"]

        if not api_summary and not web_get_all:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if web_get_all:
            try:
                return round(
                    float(web_get_all["total_hash"]["Hash Rate H"] / 1000000000000), 2
                )
            except KeyError:
                pass

        if api_summary:
            try:
                return round(float(api_summary["SUMMARY"][0]["MHS 1m"] / 1000000), 2)
            except (KeyError, IndexError):
                pass

    async def get_hashboards(
        self, api_stats: dict = None, web_get_all: dict = None
    ) -> List[HashBoard]:
        if web_get_all:
            web_get_all = web_get_all["all"]

        hashboards = [
            HashBoard(slot=i, expected_chips=self.nominal_chips)
            for i in range(self.ideal_hashboards)
        ]

        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if not web_get_all:
            try:
                web_get_all = await self.web.get_all()
            except APIError:
                pass
            else:
                web_get_all = web_get_all["all"]

        if api_stats:
            if api_stats.get("STATS"):
                for board in api_stats["STATS"]:
                    try:
                        idx = board["Chain ID"]
                        chips = board["Num active chips"]
                    except KeyError:
                        pass
                    else:
                        hashboards[idx].chips = chips
                        hashboards[idx].missing = False

        if web_get_all:
            if web_get_all.get("chain"):
                for board in web_get_all["chain"]:
                    idx = board.get("ASC")
                    if idx is not None:
                        temp = board.get("Temp min")
                        if temp:
                            hashboards[idx].temp = round(temp)

                        hashrate = board.get("Hash Rate H")
                        if hashrate:
                            hashboards[idx].hashrate = round(
                                hashrate / 1000000000000, 2
                            )

                        chip_temp = board.get("Temp max")
                        if chip_temp:
                            hashboards[idx].chip_temp = round(chip_temp)

        return hashboards

    async def get_wattage(
        self, web_get_all: dict = None, api_stats: dict = None
    ) -> Optional[int]:
        if web_get_all:
            web_get_all = web_get_all["all"]

        if not web_get_all:
            try:
                web_get_all = await self.web.get_all()
            except APIError:
                pass
            else:
                web_get_all = web_get_all["all"]

        if web_get_all:
            try:
                return web_get_all["power"]
            except KeyError:
                pass

        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            if api_stats.get("STATS"):
                for board in api_stats["STATS"]:
                    try:
                        wattage = board["power"]
                    except KeyError:
                        pass
                    else:
                        wattage = int(wattage)
                        return wattage

    async def get_fans(self, web_get_all: dict = None) -> List[Fan]:
        if web_get_all:
            web_get_all = web_get_all["all"]

        if not web_get_all:
            try:
                web_get_all = await self.web.get_all()
            except APIError:
                pass
            else:
                web_get_all = web_get_all["all"]

        fans = [Fan() for _ in range(self.fan_count)]
        if web_get_all:
            try:
                spd = web_get_all["fansSpeed"]
            except KeyError:
                pass
            else:
                round((int(spd) * 6000) / 100)
                for i in range(self.fan_count):
                    fans[i].speed = spd

        return fans

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

    async def get_errors(
        self, web_get_error_detail: dict = None
    ) -> List[MinerErrorData]:  # noqa: named this way for automatic functionality
        errors = []
        if not web_get_error_detail:
            try:
                web_get_error_detail = await self.web.get_error_detail()
            except APIError:
                pass

        if web_get_error_detail:
            try:
                # only 1 error?
                # TODO: check if this should be a loop, can't remember.
                err = web_get_error_detail["code"]
            except KeyError:
                pass
            else:
                err = int(err)
                if not err == 0:
                    errors.append(InnosiliconError(error_code=err))
        return errors

    async def get_wattage_limit(self, web_get_all: dict = None) -> Optional[int]:
        if web_get_all:
            web_get_all = web_get_all["all"]

        if not web_get_all:
            try:
                web_get_all = await self.web.get_all()
            except APIError:
                pass
            else:
                web_get_all = web_get_all["all"]

        if web_get_all:
            try:
                level = web_get_all["running_mode"]["level"]
            except KeyError:
                pass
            else:
                # this is very possibly not correct.
                level = int(level)
                limit = 1250 + (250 * level)
                return limit
