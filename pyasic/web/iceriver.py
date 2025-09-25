# ------------------------------------------------------------------------------
#  Copyright 2024 Upstream Data Inc                                            -
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
import warnings
from typing import Any

import httpx

from pyasic import settings
from pyasic.errors import APIError
from pyasic.web.base import BaseWebAPI


class IceRiverWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "admin"
        self.pwd = settings.get("default_iceriver_web_password", "12345678")

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        tasks = {c: asyncio.create_task(getattr(self, c)()) for c in commands}
        await asyncio.gather(*[t for t in tasks.values()])
        return {t: tasks[t].result() for t in tasks}

    async def send_command(
        self,
        command: str,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            try:
                # auth
                await client.post(
                    f"http://{self.ip}:{self.port}/user/loginpost",
                    params={"post": "6", "user": self.username, "pwd": self.pwd},
                )
            except httpx.HTTPError:
                warnings.warn(f"Could not authenticate with miner web: {self}")
            try:
                resp = await client.post(
                    f"http://{self.ip}:{self.port}/user/{command}", params=parameters
                )
                if not resp.status_code == 200:
                    if not ignore_errors:
                        raise APIError(f"Command failed: {command}")
                    warnings.warn(f"Command failed: {command}")
                return resp.json()
            except httpx.HTTPError:
                raise APIError(f"Command failed: {command}")

    async def locate(self, enable: bool):
        return await self.send_command(
            "userpanel", post="5", locate="1" if enable else "0"
        )

    async def userpanel(self):
        return await self.send_command("userpanel", post="4")
