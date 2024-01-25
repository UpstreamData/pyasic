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
from pyasic.errors import APIError
from pyasic.web.base import BaseWebAPI


class InnosiliconWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "admin"
        self.pwd = settings.get("default_innosilicon_web_password", "admin")
        self.token = None

    async def auth(self) -> str | None:
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            try:
                auth = await client.post(
                    f"http://{self.ip}:{self.port}/api/auth",
                    data={"username": self.username, "password": self.pwd},
                )
            except httpx.HTTPError:
                warnings.warn(f"Could not authenticate web token with miner: {self}")
            else:
                json_auth = auth.json()
                self.token = json_auth.get("jwt")
            return self.token

    async def send_command(
        self,
        command: str | bytes,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        if self.token is None:
            await self.auth()
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            for _ in range(settings.get("get_data_retries", 1)):
                try:
                    response = await client.post(
                        f"http://{self.ip}:{self.port}/api/{command}",
                        headers={"Authorization": "Bearer " + self.token},
                        timeout=settings.get("api_function_timeout", 5),
                        json=parameters,
                    )
                    json_data = response.json()
                    if (
                        not json_data.get("success")
                        and "token" in json_data
                        and json_data.get("token") == "expired"
                    ):
                        # refresh the token, retry
                        await self.auth()
                        continue
                    if not json_data.get("success"):
                        if json_data.get("msg"):
                            raise APIError(json_data["msg"])
                        elif json_data.get("message"):
                            raise APIError(json_data["message"])
                        raise APIError("Innosilicon web api command failed.")
                    return json_data
                except (httpx.HTTPError, json.JSONDecodeError):
                    pass

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        data = {k: None for k in commands}
        data["multicommand"] = True
        await self.auth()
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            for command in commands:
                try:
                    response = await client.post(
                        f"http://{self.ip}:{self.port}/api/{command}",
                        headers={"Authorization": "Bearer " + self.token},
                        timeout=settings.get("api_function_timeout", 5),
                    )
                    json_data = response.json()
                    data[command] = json_data
                except httpx.HTTPError:
                    pass
                except json.JSONDecodeError:
                    pass
                except TypeError:
                    await self.auth()
        return data

    async def reboot(self) -> dict:
        return await self.send_command("reboot")

    async def restart_cgminer(self) -> dict:
        return await self.send_command("restartCgMiner")

    async def update_pools(self, conf: dict) -> dict:
        return await self.send_command("updatePools", **conf)

    async def overview(self) -> dict:
        return await self.send_command("overview")

    async def type(self) -> dict:
        return await self.send_command("type")

    async def get_all(self) -> dict:
        return await self.send_command("getAll")

    async def get_error_detail(self) -> dict:
        return await self.send_command("getErrorDetail")

    async def pools(self) -> dict:
        return await self.send_command("pools")

    async def poweroff(self) -> dict:
        return await self.send_command("poweroff")
