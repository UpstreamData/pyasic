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
    "hashrate": {"cmd": "get_hashrate", "kwargs": {"web_summary": {"web": "summary"}}},
    "nominal_hashrate": {
        "cmd": "get_nominal_hashrate",
        "kwargs": {"web_summary": {"web": "summary"}},
    },
    "hashboards": {"cmd": "get_hashboards", "kwargs": {"web_summary": {"web": "summary"}, "web_hashrate": {"web": "hashrate"}}},
    "env_temp": {"cmd": "get_env_temp", "kwargs": {}},
    "wattage": {"cmd": "get_wattage", "kwargs": {"web_summary": {"web": "summary"}}},
    "fans": {"cmd": "get_fans", "kwargs": {"web_summary": {"web": "summary"}}},
    "fan_psu": {"cmd": "get_fan_psu", "kwargs": {}},
    "errors": {"cmd": "get_errors", "kwargs": {}},
    "fault_light": {"cmd": "get_fault_light", "kwargs": {}},
    "pools": {"cmd": "get_pools", "kwargs": {"web_summary": {"web": "summary"}}},
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
                for hb in web_summary["HBs"]:
                    hashrate += hb["Hashrate"][0]
                return round(
                    float(float(hashrate/ 1000000)), 2)
            except (IndexError, KeyError, ValueError, TypeError) as e:
                logger.error(e)
                pass
    
    async def get_nominal_hashrate(self, web_summary: dict = None) -> Optional[float]:
        # get hr from API
        if not web_summary:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary:
            try:
                hashrate = 0
                for hb in web_summary["HBs"]:
                    hashrate += hb["Hashrate"][0]/(hb["Hashrate"][1]/100)
                return round(
                    float(float(hashrate/ 1000000)), 2)
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
    
    async def get_hashboards(self, web_summary: dict = None, web_hashrate: dict= None) -> List[HashBoard]:
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
        hb_list = []
        for hb in web_summary["HBs"]:
            for hr in web_hashrate:
                if hr["Index"] == hb["Index"]:
                    num_of_chips = len(hr["Data"])
                    hashrate = hb["Hashrate"][0]
                    hb_list.append(HashBoard(slot=hb["Index"], expected_chips=num_of_chips, missing=False,hashrate=round(hashrate/1000000,2), chips=num_of_chips,temp=hb["Temperature"]))
        return hb_list

    async def is_mining(self, *args, **kwargs) -> Optional[bool]:
        return None
    
    async def get_pools(self, web_summary: dict = None) -> List[dict]:
       groups = []

       if not web_summary:
           try:
               web_summary = await self.api.summary()
           except APIError:
               pass

       if web_summary:
           try:
               pools = {}
               for i, pool in enumerate(web_summary["StratumConfigs"]):
                   pools[f"pool_{i + 1}_url"] = (
                       pool["pool"]
                       .replace("stratum+tcp://", "")
                       .replace("stratum2+tcp://", "")
                   )
                   pools[f"pool_{i + 1}_user"] = pool["login"]
                   pools["quota"] = pool["Quota"] if pool.get("Quota") else "0"

               groups.append(pools)
           except KeyError:
               pass
       return groups

    
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
