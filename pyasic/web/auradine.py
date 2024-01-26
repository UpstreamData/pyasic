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
import json
import warnings
from typing import Any

import httpx

from pyasic import settings
from pyasic.errors import APIError
from pyasic.misc import validate_command_output
from pyasic.web.base import BaseWebAPI


class AuradineWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "admin"
        self.pwd = settings.get("default_auradine_web_password", "admin")
        self.port = 8080
        self.token = None

    async def auth(self) -> str | None:
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            try:
                auth = await client.post(
                    f"http://{self.ip}:{self.port}/token",
                    json={
                        "command": "token",
                        "user": self.username,
                        "password": self.pwd,
                    },
                )
            except httpx.HTTPError:
                warnings.warn(f"Could not authenticate web token with miner: {self}")
            else:
                json_auth = auth.json()
                try:
                    self.token = json_auth["Token"][0]["Token"]
                except LookupError:
                    return None
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
        if not parameters == {}:
            parameters["command"] = command

        if self.token is None:
            await self.auth()
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            for i in range(settings.get("get_data_retries", 1)):
                try:
                    if post:
                        response = await client.post(
                            f"http://{self.ip}:{self.port}/{command}",
                            headers={"Token": self.token},
                            timeout=settings.get("api_function_timeout", 5),
                            json=parameters,
                        )
                    else:
                        response = await client.get(
                            f"http://{self.ip}:{self.port}/{command}",
                            headers={"Token": self.token},
                            timeout=settings.get("api_function_timeout", 5),
                        )
                    json_data = response.json()
                    validation = validate_command_output(json_data)
                    if not validation[0]:
                        if i == settings.get("get_data_retries", 1):
                            raise APIError(validation[1])
                        # refresh the token, retry
                        await self.auth()
                        continue
                    return json_data
                except (httpx.HTTPError, json.JSONDecodeError):
                    pass

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        tasks = {}
        # send all commands individually
        for cmd in commands:
            tasks[cmd] = asyncio.create_task(
                self.send_command(cmd, allow_warning=allow_warning)
            )

        await asyncio.gather(*[tasks[cmd] for cmd in tasks], return_exceptions=True)

        data = {"multicommand": True}
        for cmd in tasks:
            try:
                result = tasks[cmd].result()
                if result is None or result == {}:
                    result = {}
                data[cmd] = result
            except APIError:
                pass

        return data

    async def factory_reset(self) -> dict:
        return await self.send_command("factory-reset", privileged=True)

    async def get_fan(self) -> dict:
        return await self.send_command("fan")

    async def set_fan(self, fan: int, speed_pct: int) -> dict:
        return await self.send_command("fan", index=fan, percentage=speed_pct)

    async def firmware_upgrade(self, url: str = None, version: str = "latest") -> dict:
        if url is not None:
            return await self.send_command("firmware-upgrade", url=url)
        return await self.send_command("firmware-upgrade", version=version)

    async def get_frequency(self) -> dict:
        return await self.send_command("frequency")

    async def set_frequency(self, board: int, frequency: float) -> dict:
        return await self.send_command("frequency", board=board, frequency=frequency)

    async def ipreport(self) -> dict:
        return await self.send_command("ipreport")

    async def get_led(self) -> dict:
        return await self.send_command("led")

    async def set_led(self, code: int) -> dict:
        return await self.send_command("led", code=code)

    async def set_led_custom(self, code: int, led_1: int, led_2: int, msg: str) -> dict:
        return await self.send_command(
            "led", code=code, led1=led_1, led2=led_2, msg=msg
        )

    async def get_mode(self) -> dict:
        return await self.send_command("mode")

    async def set_mode(self, **kwargs) -> dict:
        return await self.send_command("mode", **kwargs)

    async def get_network(self) -> dict:
        return await self.send_command("network")

    async def set_network(self, **kwargs) -> dict:
        return await self.send_command("network", **kwargs)

    async def password(self, password: str) -> dict:
        res = await self.send_command(
            "password", user=self.username, old=self.pwd, new=password
        )
        self.pwd = password
        return res

    async def get_psu(self) -> dict:
        return await self.send_command("psu")

    async def set_psu(self, voltage: float) -> dict:
        return await self.send_command("psu", voltage=voltage)

    async def get_register(self) -> dict:
        return await self.send_command("register")

    async def set_register(self, company: str) -> dict:
        return await self.send_command("register", parameter=company)

    async def reboot(self) -> dict:
        return await self.send_command("restart", privileged=True)

    async def restart_gcminer(self) -> dict:
        return await self.send_command("restart", parameter="gcminer")

    async def restart_api_server(self) -> dict:
        return await self.send_command("restart", parameter="api-server")

    async def temperature(self) -> dict:
        return await self.send_command("temperature")

    async def timedate(self, ntp: str, timezone: str) -> dict:
        return await self.send_command("timedate", ntp=ntp, timezone=timezone)

    async def get_token(self) -> dict:
        return await self.send_command("token", user=self.username, password=self.pwd)

    async def update_pools(self, pools: list[dict]) -> dict:
        return await self.send_command("updatepools", pools=pools)

    async def voltage(self) -> dict:
        return await self.send_command("voltage")

    async def get_ztp(self) -> dict:
        return await self.send_command("ztp")

    async def set_ztp(self, enable: bool) -> dict:
        return await self.send_command("ztp", parameter="on" if enable else "off")
