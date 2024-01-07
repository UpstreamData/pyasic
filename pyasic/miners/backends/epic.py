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

from typing import List, Optional, Tuple


from pyasic import MinerConfig
from pyasic.data import Fan, HashBoard
from pyasic.data.error_codes import MinerErrorData, X19Error
from pyasic.config import MinerConfig, MiningModeConfig
from pyasic.errors import APIError
from pyasic.logger import logger
from pyasic.miners.base import (
    BaseMiner,
    DataFunction,
    DataLocations,
    DataOptions,
    WebAPICommand,
)
from pyasic.web.epic import ePICWebAPI

EPIC_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "get_mac", [WebAPICommand("web_network", "network")]
        ),
        str(DataOptions.MODEL): DataFunction("get_model"),
        str(DataOptions.API_VERSION): DataFunction("get_api_ver"),
        str(DataOptions.FW_VERSION): DataFunction(
            "get_fw_ver", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "get_hostname", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "get_hashrate", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "get_expected_hashrate", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "get_hashboards",
            [
                WebAPICommand("web_summary", "summary"),
                WebAPICommand("web_hashrate", "hashrate"),
            ],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction("get_env_temp"),
        str(DataOptions.WATTAGE): DataFunction(
            "get_wattage", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction("get_wattage_limit"),
        str(DataOptions.FANS): DataFunction(
            "get_fans", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.FAN_PSU): DataFunction("get_fan_psu"),
        str(DataOptions.ERRORS): DataFunction(
            "get_errors", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "get_fault_light", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.IS_MINING): DataFunction("is_mining"),
        str(DataOptions.UPTIME): DataFunction(
            "get_uptime", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.CONFIG): DataFunction("get_config"),
    }
)


class ePIC(BaseMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver)
        # interfaces
        self.web = ePICWebAPI(ip)

        # static data
        self.api_type = "ePIC"
        # data gathering locations
        self.data_locations = EPIC_DATA_LOC

    async def get_model(self) -> Optional[str]:
        if self.model is not None:
            return self.model + " (ePIC)"
        return "? (ePIC)"

    async def get_config(self) -> MinerConfig:
        summary = None
        try:
            summary = await self.web.summary()
        except APIError as e:
            logger.warning(e)
        except LookupError:
            pass

        if summary is not None:
            cfg = MinerConfig.from_epic(summary)
        else:
            cfg = MinerConfig()

        self.config = cfg
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config
        conf = self.config.as_epic(user_suffix=user_suffix)

        try:
            # Temps
            data = await self.web.set_shutdown_temp(conf["temp_control"]["hot_temp"])
            # Fans
            if conf["fan_control"]["mode"] == "Manual":
                data = await self.web.set_fan(
                    {"Manual": int(conf["fan_control"]["speed"])}
                )
            if conf["fan_control"]["mode"] == "Auto":
                data = await self.web.set_fan(
                    {
                        "Auto": {
                            "Idle Speed": int(conf["fan_control"]["speed"]),
                            "Target Temperature": int(
                                conf["temp_control"]["target_temp"]
                            ),
                        }
                    }
                )

            ## Mining Mode -- Need to handle that you may not be able to change while miner is tuning
            if conf["ptune"]["enabled"] == True:
                data = await self.web.set_ptune_enable(True)
                data = await self.web.set_ptune_algo(
                    {"algo": conf["ptune"]["algo"], "target": conf["ptune"]["target"]}
                )

            ## Pools
            update_pool_configs = []
            for group in conf["pools"]:
                for pool_config in group["pool"]:
                    update_pool_configs.append(pool_config)
            data = await self.web.set_pools(
                {
                    "coin": "Btc",
                    "stratum_configs": update_pool_configs,
                    "unique_id": True,
                }
            )
        except APIError:
            pass

    async def restart_backend(self) -> bool:
        data = await self.web.restart_epic()
        if data:
            try:
                return data["success"]
            except KeyError:
                pass
        return False

    async def stop_mining(self) -> bool:
        data = await self.web.stop_mining()
        if data:
            try:
                return data["success"]
            except KeyError:
                pass
        return False

    async def resume_mining(self) -> bool:
        data = await self.web.resume_mining()
        if data:
            try:
                return data["success"]
            except KeyError:
                pass
        return False

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            try:
                return data["success"]
            except KeyError:
                pass
        return False

    async def get_mac(self, web_network: dict = None) -> str:
        if not web_network:
            web_network = await self.web.network()
        if web_network:
            try:
                for network in web_network:
                    mac = web_network[network]["mac_address"]
                return mac
            except KeyError:
                pass

    async def get_hostname(self, web_summary: dict = None) -> str:
        if not web_summary:
            web_summary = await self.web.summary()
        if web_summary:
            try:
                hostname = web_summary["Hostname"]
                return hostname
            except KeyError:
                pass

    async def get_wattage(self, web_summary: dict = None) -> Optional[int]:
        if not web_summary:
            web_summary = await self.web.summary()

        if web_summary:
            try:
                wattage = web_summary["Power Supply Stats"]["Input Power"]
                wattage = round(wattage)
                return wattage
            except KeyError:
                pass

    async def get_hashrate(self, web_summary: dict = None) -> Optional[float]:
        # get hr from API
        if not web_summary:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary:
            try:
                hashrate = 0
                if web_summary["HBs"] != None:
                    for hb in web_summary["HBs"]:
                        hashrate += hb["Hashrate"][0]
                    return round(float(float(hashrate / 1000000)), 2)
            except (LookupError, ValueError, TypeError) as e:
                logger.error(e)
                pass

    async def get_expected_hashrate(self, web_summary: dict = None) -> Optional[float]:
        # get hr from API
        if not web_summary:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary:
            try:
                hashrate = 0
                if web_summary["HBs"] != None:
                    for hb in web_summary["HBs"]:
                        if hb["Hashrate"][1] == 0:
                            ideal = 1.0
                        else:
                            ideal = hb["Hashrate"][1] / 100

                        hashrate += hb["Hashrate"][0] / ideal
                    return round(float(float(hashrate / 1000000)), 2)
            except (IndexError, KeyError, ValueError, TypeError) as e:
                logger.error(e)
                pass

    async def get_fw_ver(self, web_summary: dict = None) -> Optional[str]:
        if not web_summary:
            web_summary = await self.web.summary()

        if web_summary:
            try:
                fw_ver = web_summary["Software"]
                fw_ver = fw_ver.split(" ")[1].replace("v", "")
                return fw_ver
            except KeyError:
                pass

    async def get_fans(self, web_summary: dict = None) -> List[Fan]:
        if not web_summary:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        fans = []

        if web_summary:
            for fan in web_summary["Fans Rpm"]:
                try:
                    fans.append(Fan(web_summary["Fans Rpm"][fan]))
                except (LookupError, ValueError, TypeError):
                    fans.append(Fan())
        return fans

    async def get_hashboards(
        self, web_summary: dict = None, web_hashrate: dict = None
    ) -> List[HashBoard]:
        if not web_summary:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass
        if not web_hashrate:
            try:
                web_hashrate = await self.web.hashrate()
            except APIError:
                pass
        hb_list = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]
        if web_summary["HBs"] != None:
            for hb in web_summary["HBs"]:
                for hr in web_hashrate:
                    if hr["Index"] == hb["Index"]:
                        num_of_chips = len(hr["Data"])
                        hashrate = hb["Hashrate"][0]
                        # Update the Hashboard object
                        hb_list[hr["Index"]].expected_chips = num_of_chips
                        hb_list[hr["Index"]].missing = False
                        hb_list[hr["Index"]].hashrate = round(hashrate / 1000000, 2)
                        hb_list[hr["Index"]].chips = num_of_chips
                        hb_list[hr["Index"]].temp = hb["Temperature"]
        return hb_list

    async def is_mining(self, *args, **kwargs) -> Optional[bool]:
        return None

    async def get_uptime(self, web_summary: dict = None) -> Optional[int]:
        if not web_summary:
            web_summary = await self.web.summary()
        if web_summary:
            try:
                uptime = web_summary["Session"]["Uptime"]
                return uptime
            except KeyError:
                pass
        return None

    async def get_fault_light(self, web_summary: dict = None) -> bool:
        if not web_summary:
            web_summary = await self.web.summary()
        if web_summary:
            try:
                light = web_summary["Misc"]["Locate Miner State"]
                return light
            except KeyError:
                pass
        return False

    async def get_errors(self, web_summary: dict = None) -> List[MinerErrorData]:
        if not web_summary:
            web_summary = await self.web.summary()
        errors = []
        if web_summary:
            try:
                error = web_summary["Status"]["Last Error"]
                if error != None:
                    errors.append(X19Error(str(error)))
                return errors
            except KeyError:
                pass
        return errors

    def fault_light_off(self) -> bool:
        return False

    def fault_light_on(self) -> bool:
        return False

    def get_api_ver(self, *args, **kwargs) -> Optional[str]:
        pass

    def get_env_temp(self, *args, **kwargs) -> Optional[float]:
        pass

    def get_fan_psu(self, *args, **kwargs) -> Optional[int]:
        pass

    def get_version(self, *args, **kwargs) -> Tuple[Optional[str], Optional[str]]:
        pass

    def get_wattage_limit(self, *args, **kwargs) -> Optional[int]:
        pass

    def set_power_limit(self, wattage: int) -> bool:
        return False
