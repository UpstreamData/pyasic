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
from pyasic.web.epic import ePICWebAPI
from pyasic.data import Fan, HashBoard
from typing import List, Optional, Tuple, Union


EPIC_DATA_LOC = {
    "mac": {"cmd": "get_mac", "kwargs": {"web_summary": {"web": "network"}}},
    "model": {"cmd": "get_model", "kwargs": {}},
    "api_ver": {"cmd": "get_api_ver", "kwargs": {"api_version": {"api": "version"}}},
    "fw_ver": {"cmd": "get_fw_ver", "kwargs": {"web_summary": {"web": "summary"}}},
    "hostname": {"cmd": "get_hostname", "kwargs": {"web_summary": {"web": "summary"}}},
    "hashrate": {"cmd": "get_hashrate", "kwargs": {"api_summary": {"api": "summary"}}},
    "nominal_hashrate": {
        "cmd": "get_nominal_hashrate",
        "kwargs": {"api_stats": {"api": "stats"}},
    },
    "hashboards": {"cmd": "get_hashboards", "kwargs": {"api_stats": {"api": "stats"}}},
    "env_temp": {"cmd": "get_env_temp", "kwargs": {}},
    "wattage": {"cmd": "get_wattage", "kwargs": {"web_summary": {"web": "summary"}}},
    "fans": {"cmd": "get_fans", "kwargs": {"web_summary": {"web": "summary"}}},
    "fan_psu": {"cmd": "get_fan_psu", "kwargs": {}},
    "errors": {"cmd": "get_errors", "kwargs": {}},
    "fault_light": {"cmd": "get_fault_light", "kwargs": {}},
    "pools": {"cmd": "get_pools", "kwargs": {"api_pools": {"api": "pools"}}},
    "is_mining": {"cmd": "is_mining", "kwargs": {}},
    "uptime": {"cmd": "get_uptime", "kwargs": {"web_summary": {"web": "summary"}}},
}


class ePIC(BMMiner):
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

    async def get_mac(self, web_summary: dict = None) -> str:
        if not web_summary:
            web_summary = await self.web.network()
        if web_summary:
            try:
                for network in web_summary:
                    mac = web_summary[network]["mac_address"]
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

    async def get_hashrate(self, api_summary: dict = None) -> Optional[float]:
        # get hr from API
        if not api_summary:
            try:
                api_summary = await self.web.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return round(
                    float(float(api_summary["Session"]["Average MHs"]) / 1000000), 2
                )
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
                except (IndexError, KeyError, ValueError, TypeError):
                    fans.append(Fan())
        return fans

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
