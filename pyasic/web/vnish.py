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

import json
import warnings
from typing import Any

import httpx

from pyasic import settings
from pyasic.web.base import BaseWebAPI


class VNishWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "admin"
        self.pwd = settings.get("default_vnish_web_password", "admin")
        self.token = None

    async def auth(self) -> str | None:
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            try:
                auth = await client.post(
                    f"http://{self.ip}:{self.port}/api/v1/unlock",
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
                self.token = json_auth["token"]
            return self.token

    async def send_command(
        self,
        command: str | bytes,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        post = privileged or not parameters == {}
        if self.token is None:
            await self.auth()
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            for _ in range(settings.get("get_data_retries", 1)):
                try:
                    auth = self.token
                    if command.startswith("system"):
                        auth = "Bearer " + self.token

                    if post:
                        response = await client.post(
                            f"http://{self.ip}:{self.port}/api/v1/{command}",
                            headers={"Authorization": auth},
                            timeout=settings.get("api_function_timeout", 5),
                            json=parameters,
                        )
                    else:
                        response = await client.get(
                            f"http://{self.ip}:{self.port}/api/v1/{command}",
                            headers={"Authorization": auth},
                            timeout=settings.get("api_function_timeout", 5),
                        )
                    if not response.status_code == 200:
                        # refresh the token, retry
                        await self.auth()
                        continue
                    json_data = response.json()
                    if json_data:
                        return json_data
                    return {"success": True}
                except (httpx.HTTPError, json.JSONDecodeError, AttributeError):
                    pass

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        data = {k: None for k in commands}
        data["multicommand"] = True
        for command in commands:
            data[command] = await self.send_command(command)
        return data

    async def restart_vnish(self) -> dict:
        return await self.send_command("mining/restart", privileged=True)

    async def reboot(self) -> dict:
        return await self.send_command("system/reboot", privileged=True)

    async def pause_mining(self) -> dict:
        return await self.send_command("mining/pause", privileged=True)

    async def resume_mining(self) -> dict:
        return await self.send_command("mining/resume", privileged=True)

    async def stop_mining(self) -> dict:
        return await self.send_command("mining/stop", privileged=True)

    async def start_mining(self) -> dict:
        return await self.send_command("mining/start", privileged=True)

    async def info(self) -> dict:
        return await self.send_command("info")

    async def summary(self) -> dict:
        return await self.send_command("summary")

    async def chips(self) -> dict:
        return await self.send_command("chips")

    async def layout(self) -> dict:
        return await self.send_command("layout")

    async def status(self) -> dict:
        return await self.send_command("status")

    async def settings(self) -> dict:
        return await self.send_command("settings")

    async def autotune_presets(self) -> dict:
        return await self.send_command("autotune/presets")
