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
from pyasic.data.error_codes import MinerErrorData
from pyasic.data.error_codes.innosilicon import InnosiliconError
from pyasic.errors import APIError
from pyasic.miners.backends import CGMiner
from pyasic.miners.base import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.web.innosilicon import InnosiliconWebAPI

INNOSILICON_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [
                WebAPICommand("web_get_all", "getAll"),
                WebAPICommand("web_overview", "overview"),
            ],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver", [RPCAPICommand("api_version", "version")]
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver", [RPCAPICommand("api_version", "version")]
        ),
        str(DataOptions.HOSTNAME): DataFunction("_get_hostname"),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [
                RPCAPICommand("api_summary", "summary"),
                WebAPICommand("web_get_all", "getAll"),
            ],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [
                RPCAPICommand("api_stats", "stats"),
                WebAPICommand("web_get_all", "getAll"),
            ],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction("_get_env_temp"),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [
                WebAPICommand("web_get_all", "getAll"),
                RPCAPICommand("api_stats", "stats"),
            ],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [
                WebAPICommand("web_get_all", "getAll"),
            ],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [
                WebAPICommand("web_get_all", "getAll"),
            ],
        ),
        str(DataOptions.FAN_PSU): DataFunction("_get_fan_psu"),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [
                WebAPICommand("web_get_error_detail", "getErrorDetail"),
            ],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction("_get_fault_light"),
        str(DataOptions.IS_MINING): DataFunction("_is_mining"),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime", [RPCAPICommand("api_stats", "stats")]
        ),
        str(DataOptions.CONFIG): DataFunction("get_config"),
    }
)


class Innosilicon(CGMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        # interfaces
        self.web = InnosiliconWebAPI(ip)

        # static data
        # data gathering locations
        self.data_locations = INNOSILICON_DATA_LOC
        # autotuning/shutdown support
        self.supports_shutdown = True

        # data storage
        self.api_ver = api_ver

    async def fault_light_on(self) -> bool:
        return False

    async def fault_light_off(self) -> bool:
        return False

    async def get_config(self) -> MinerConfig:
        # get pool data
        try:
            pools = await self.web.pools()
        except APIError:
            return self.config

        self.config = MinerConfig.from_inno(pools)
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

    async def stop_mining(self) -> bool:
        return False
        # data = await self.web.poweroff()
        # try:
        #     return data["success"]
        # except KeyError:
        #     return False

    async def resume_mining(self) -> bool:
        return False
        # data = await self.web.restart_cgminer()
        # print(data)
        # try:
        #     return data["success"]
        # except KeyError:
        #     return False

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config
        await self.web.update_pools(config.as_inno(user_suffix=user_suffix))

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(
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

    async def _get_hashrate(
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
                if "Hash Rate H" in web_get_all["total_hash"].keys():
                    return round(
                        float(web_get_all["total_hash"]["Hash Rate H"] / 1000000000000),
                        2,
                    )
                elif "Hash Rate" in web_get_all["total_hash"].keys():
                    return round(
                        float(web_get_all["total_hash"]["Hash Rate"] / 1000000), 5
                    )
            except KeyError:
                pass

        if api_summary:
            try:
                return round(float(api_summary["SUMMARY"][0]["MHS 1m"] / 1000000), 2)
            except (KeyError, IndexError):
                pass

    async def _get_hashboards(
        self, api_stats: dict = None, web_get_all: dict = None
    ) -> List[HashBoard]:
        if web_get_all:
            web_get_all = web_get_all["all"]

        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
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

    async def _get_wattage(
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

    async def _get_fans(self, web_get_all: dict = None) -> List[Fan]:
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

    async def _get_errors(
        self, web_get_error_detail: dict = None
    ) -> List[MinerErrorData]:
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

    async def _get_wattage_limit(self, web_get_all: dict = None) -> Optional[int]:
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

    async def _get_expected_hashrate(self) -> Optional[float]:
        pass
