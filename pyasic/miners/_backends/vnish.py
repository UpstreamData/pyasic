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

import json
import logging
import warnings
from typing import Optional, Union

import httpx

from pyasic.errors import APIError
from pyasic.miners._backends.bmminer import BMMiner
from pyasic.settings import PyasicSettings


class VNish(BMMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver)
        self.api_type = "VNish"
        self.uname = "root"
        self.pwd = PyasicSettings().global_vnish_password
        self.jwt = None

    async def auth(self):
        async with httpx.AsyncClient() as client:
            try:
                auth = await client.post(
                    f"http://{self.ip}/api/v1/unlock",
                    json={"pw": self.pwd},
                )
            except httpx.HTTPError:
                warnings.warn(f"Could not authenticate web token with miner: {self}")
            else:
                if not auth.status_code == 200:
                    warnings.warn(
                        f"Could not authenticate web token with miner: {self}"
                    )
                    return None
                json_auth = auth.json()
                self.jwt = json_auth["token"]
            return self.jwt

    async def send_web_command(
        self, command: str, data: Union[dict, None] = None, method: str = "GET"
    ):
        if not self.jwt:
            await self.auth()
        if not data:
            data = {}
        async with httpx.AsyncClient() as client:
            for i in range(PyasicSettings().miner_get_data_retries):
                try:
                    auth = self.jwt
                    if command.startswith("system"):
                        auth = "Bearer " + self.jwt
                    if method == "GET":
                        response = await client.get(
                            f"http://{self.ip}/api/v1/{command}",
                            headers={"Authorization": auth},
                            timeout=5,
                        )
                    elif method == "POST":
                        if data:
                            response = await client.post(
                                f"http://{self.ip}/api/v1/{command}",
                                headers={"Authorization": auth},
                                timeout=5,
                                json=data,
                            )
                        else:
                            response = await client.post(
                                f"http://{self.ip}/api/v1/{command}",
                                headers={"Authorization": auth},
                                timeout=5,
                            )
                    else:
                        raise APIError("Bad method type.")
                    if not response.status_code == 200:
                        # refresh the token, retry
                        await self.auth()
                        continue
                    json_data = response.json()
                    if json_data:
                        return json_data
                    return True
                except httpx.HTTPError:
                    pass
                except json.JSONDecodeError:
                    pass

    async def get_model(self, api_stats: dict = None) -> Optional[str]:
        # check if model is cached
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model} (VNish)")
            return self.model + " (VNish)"

        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            try:
                m_type = api_stats["STATS"][0]["Type"]
                self.model = m_type.split(" ")[1]
                return self.model
            except (KeyError, IndexError):
                pass

    async def restart_backend(self) -> bool:
        data = await self.send_web_command("mining/restart", method="POST")
        return data

    async def reboot(self) -> bool:
        data = await self.send_web_command("system/reboot", method="POST")
        return data

    async def get_mac(self, web_summary: dict = None) -> str:
        if not web_summary:
            web_info = await self.send_web_command("info")

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
            web_info = await self.send_web_command("info")

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
            web_summary = await self.send_web_command("summary")

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
                print(e)
                pass

    async def get_wattage_limit(self, web_settings: dict = None) -> Optional[int]:
        if not web_settings:
            web_settings = await self.send_web_command("summary")

        if web_settings:
            try:
                wattage_limit = web_settings["miner"]["overclock"]["preset"]
                return int(wattage_limit)
            except (KeyError, TypeError):
                pass

    async def get_fw_ver(self, web_summary: dict = None) -> Optional[str]:
        if not web_summary:
            web_summary = await self.send_web_command("summary")

        if web_summary:
            try:
                fw_ver = web_summary["miner"]["miner_type"]
                fw_ver = fw_ver.split("(Vnish ")[1].replace(")", "")
                return fw_ver
            except KeyError:
                pass
