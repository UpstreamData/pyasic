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
from typing import Any, TypedDict

import httpx

from pyasic import settings
from pyasic.errors import APIError
from pyasic.web.base import BaseWebAPI

PoolPass = TypedDict("PoolPass", {"pass": str})


class GoldshellWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username: str = "admin"
        self.pwd: str = settings.get("default_goldshell_web_password", "123456789")
        self.token: str | None = None

    async def auth(self) -> str | None:
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            try:
                await client.get(f"http://{self.ip}:{self.port}/user/logout")
                auth = (
                    await client.get(
                        f"http://{self.ip}:{self.port}/user/login?username={self.username}&password={self.pwd}&cipher=false"
                    )
                ).json()
            except httpx.HTTPError:
                warnings.warn(f"Could not authenticate web token with miner: {self}")
            except json.JSONDecodeError:
                # try again with encrypted normal password
                try:
                    auth = (
                        await client.get(
                            f"http://{self.ip}:{self.port}/user/login?username=admin&password=bbad7537f4c8b6ea31eea0b3d760e257&cipher=true"
                        )
                    ).json()
                except (httpx.HTTPError, json.JSONDecodeError):
                    warnings.warn(
                        f"Could not authenticate web token with miner: {self}"
                    )
                else:
                    self.token = auth.get("JWT Token")
            else:
                self.token = auth.get("JWT Token")
            return self.token

    async def send_command(
        self,
        command: str,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        if self.token is None:
            await self.auth()
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            retries = settings.get("get_data_retries", 1)
            for attempt in range(retries):
                if self.token is None:
                    raise APIError(
                        f"Could not authenticate web token with miner: {self}"
                    )
                try:
                    if not parameters == {}:
                        response = await client.put(
                            f"http://{self.ip}:{self.port}/mcb/{command}",
                            headers={"Authorization": "Bearer " + self.token},
                            timeout=settings.get("api_function_timeout", 5),
                            json=parameters,
                        )
                    else:
                        response = await client.get(
                            f"http://{self.ip}:{self.port}/mcb/{command}",
                            headers={"Authorization": "Bearer " + self.token},
                            timeout=settings.get("api_function_timeout", 5),
                        )
                    json_data = response.json()
                    return json_data
                except TypeError:
                    await self.auth()
                except httpx.HTTPError as e:
                    if attempt == retries - 1:
                        raise APIError(
                            f"HTTP error sending '{command}' to {self.ip}: {e}"
                        )
                except json.JSONDecodeError as e:
                    if attempt == retries - 1:
                        response_text = (
                            response.text if response.text else "empty response"
                        )
                        raise APIError(
                            f"JSON decode error for '{command}' from {self.ip}: {e} - Response: {response_text}"
                        )
        raise APIError(f"Failed to send command to miner: {self}")

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        data: dict[str, Any] = {k: None for k in commands}
        data["multicommand"] = True
        await self.auth()
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            for command in commands:
                if self.token is None:
                    raise APIError(
                        f"Could not authenticate web token with miner: {self}"
                    )
                try:
                    uri_commnand = command
                    if command == "devs":
                        uri_commnand = "cgminer?cgminercmd=devs"

                    response = await client.get(
                        f"http://{self.ip}:{self.port}/mcb/{uri_commnand}",
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

    async def pools(self) -> dict:
        return await self.send_command("pools")

    async def newpool(self, url: str, user: str, password: str) -> dict:
        # looks dumb, but cant pass `pass` since it is a built in type
        poolpass: PoolPass = {"pass": password}
        return await self.send_command("newpool", url=url, user=user, **poolpass)

    async def delpool(
        self, url: str, user: str, password: str, dragid: int = 0
    ) -> dict:
        # looks dumb, but cant pass `pass` since it is a built in type
        poolpass: PoolPass = {"pass": password}
        return await self.send_command(
            "delpool", url=url, user=user, dragid=dragid, **poolpass
        )

    async def setting(self) -> dict:
        return await self.send_command("setting")

    async def set_setting(self, values: dict) -> None:
        await self.send_command("setting", **values)

    async def status(self) -> dict:
        return await self.send_command("status")

    async def devs(self) -> dict:
        return await self.send_command("cgminer?cgminercmd=devs")
