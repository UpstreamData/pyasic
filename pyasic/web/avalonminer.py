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
from __future__ import annotations

import asyncio
import hashlib
import json
from typing import Any

import httpx

from pyasic import settings
from pyasic.web.base import BaseWebAPI


class AvalonMinerWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        """Initialize the modern Avalonminer API client with a specific IP address.

        Args:
            ip (str): IP address of the Avalonminer device.
        """
        super().__init__(ip)
        self.username: str = "root"
        self.pwd: str = settings.get("default_avalonminer_web_password", "root")

    async def send_command(
        self,
        command: str,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        """Send a command to the Avalonminer device using HTTP digest authentication.

        Args:
            command (str): The CGI command to send.
            ignore_errors (bool): If True, ignore any HTTP errors.
            allow_warning (bool): If True, proceed with warnings.
            **parameters: Arbitrary keyword arguments to be sent as parameters in the request.

        Returns:
            dict: The JSON response from the device or an empty dictionary if an error occurs.
        """
        cookie_data = "ff0000ff" + hashlib.sha256(self.pwd.encode()).hexdigest()[:24]

        url = f"http://{self.ip}:{self.port}/{command}.cgi"
        try:
            async with httpx.AsyncClient(transport=settings.transport()) as client:
                client.cookies.set("auth", cookie_data)
                resp = await client.get(url)
                raw_data = resp.text.replace("minerinfoCallback(", "").replace(");", "")
                return json.loads(raw_data)
        except (httpx.HTTPError, json.JSONDecodeError):
            pass
        return {}

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            cookie_data = (
                "ff0000ff" + hashlib.sha256(self.pwd.encode()).hexdigest()[:24]
            )
            client.cookies.set("auth", cookie_data)
            tasks = [
                asyncio.create_task(self._handle_multicommand(client, command))
                for command in commands
            ]
            all_data = await asyncio.gather(*tasks)

        data = {}
        for item in all_data:
            data.update(item)

        data["multicommand"] = True
        return data

    async def _handle_multicommand(
        self, client: httpx.AsyncClient, command: str
    ) -> dict:
        try:
            url = f"http://{self.ip}:{self.port}/{command}.cgi"
            resp = await client.get(url)
            raw_data = resp.text.replace("minerinfoCallback(", "").replace(");", "")
            return json.loads(raw_data)
        except httpx.HTTPError:
            pass
        return {}

    async def minerinfo(self):
        return await self.send_command("get_minerinfo")

    async def home(self):
        return await self.send_command("get_home")
