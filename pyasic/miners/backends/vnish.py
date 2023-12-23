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

from typing import Optional

from pyasic.errors import APIError
from pyasic.logger import logger
from pyasic.miners.backends.bmminer import BMMiner
from pyasic.miners.base import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.web.vnish import VNishWebAPI

VNISH_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "get_mac", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.MODEL): DataFunction("get_model"),
        str(DataOptions.API_VERSION): DataFunction(
            "get_api_ver", [RPCAPICommand("api_version", "version")]
        ),
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
            "get_expected_hashrate", [RPCAPICommand("api_stats", "stats")]
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "get_hashboards", [RPCAPICommand("api_stats", "stats")]
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction("get_env_temp"),
        str(DataOptions.WATTAGE): DataFunction(
            "get_wattage", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "get_wattage_limit", [WebAPICommand("web_settings", "settings")]
        ),
        str(DataOptions.FANS): DataFunction(
            "get_fans", [WebAPICommand("web_summary", "summary")]
        ),
        str(DataOptions.FAN_PSU): DataFunction("get_fan_psu"),
        str(DataOptions.ERRORS): DataFunction("get_errors"),
        str(DataOptions.FAULT_LIGHT): DataFunction("get_fault_light"),
        str(DataOptions.IS_MINING): DataFunction("is_mining"),
        str(DataOptions.UPTIME): DataFunction("get_uptime"),
        str(DataOptions.CONFIG): DataFunction("get_config"),
    }
)


class VNish(BMMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver)
        # interfaces
        self.web = VNishWebAPI(ip)

        # static data
        self.api_type = "VNish"
        # data gathering locations
        self.data_locations = VNISH_DATA_LOC

    async def get_model(self) -> Optional[str]:
        if self.model is not None:
            return self.model + " (VNish)"
        return "? (VNish)"

    async def restart_backend(self) -> bool:
        data = await self.web.restart_vnish()
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

    async def get_mac(self, web_summary: dict = None) -> str:
        if not web_summary:
            web_info = await self.web.info()

            if web_info:
                try:
                    mac = web_info["system"]["network_status"]["mac"]
                    return mac
                except KeyError:
                    pass

        if web_summary:
            try:
                mac = web_summary["system"]["network_status"]["mac"]
                return mac
            except KeyError:
                pass

    async def get_hostname(self, web_summary: dict = None) -> str:
        if not web_summary:
            web_info = await self.web.info()

            if web_info:
                try:
                    hostname = web_info["system"]["network_status"]["hostname"]
                    return hostname
                except KeyError:
                    pass

        if web_summary:
            try:
                hostname = web_summary["system"]["network_status"]["hostname"]
                return hostname
            except KeyError:
                pass

    async def get_wattage(self, web_summary: dict = None) -> Optional[int]:
        if not web_summary:
            web_summary = await self.web.summary()

        if web_summary:
            try:
                wattage = web_summary["miner"]["power_usage"]
                wattage = round(wattage * 1000)
                return wattage
            except KeyError:
                pass

    async def get_hashrate(self, api_summary: dict = None) -> Optional[float]:
        # get hr from API
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return round(
                    float(float(api_summary["SUMMARY"][0]["GHS 5s"]) / 1000), 2
                )
            except (IndexError, KeyError, ValueError, TypeError) as e:
                logger.error(e)
                pass

    async def get_wattage_limit(self, web_settings: dict = None) -> Optional[int]:
        if not web_settings:
            web_settings = await self.web.summary()

        if web_settings:
            try:
                wattage_limit = web_settings["miner"]["overclock"]["preset"]
                if wattage_limit == "disabled":
                    return None
                return int(wattage_limit)
            except (KeyError, TypeError):
                pass

    async def get_fw_ver(self, web_summary: dict = None) -> Optional[str]:
        if not web_summary:
            web_summary = await self.web.summary()

        if web_summary:
            try:
                fw_ver = web_summary["miner"]["miner_type"]
                fw_ver = fw_ver.split("(Vnish ")[1].replace(")", "")
                return fw_ver
            except KeyError:
                pass

    async def is_mining(self, *args, **kwargs) -> Optional[bool]:
        return None

    async def get_uptime(self, *args, **kwargs) -> Optional[int]:
        return None
