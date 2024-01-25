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
import asyncio
import json
import warnings
from typing import Any, List, Union

import httpx

from pyasic import settings
from pyasic.errors import APIError
from pyasic.web import BaseWebAPI


class FluxWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "admin"
        self.pwd = settings.get("default_auradine_web_password", "admin")
        self.port = 8080
        self.jwt = None

    async def auth(self):
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
                    self.jwt = json_auth["Token"][0]["Token"]
                except LookupError:
                    return None
            return self.jwt

    async def send_command(
        self,
        command: Union[str, bytes],
        post: bool = False,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Any,
    ) -> dict:
        if self.jwt is None:
            await self.auth()
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            for i in range(settings.get("get_data_retries", 1)):
                try:
                    if post:
                        response = await client.post(
                            f"http://{self.ip}:{self.port}/{command}",
                            headers={"Token": self.jwt},
                            timeout=settings.get("api_function_timeout", 5),
                        )
                    elif parameters:
                        response = await client.post(
                            f"http://{self.ip}:{self.port}/{command}",
                            headers={"Token": self.jwt},
                            timeout=settings.get("api_function_timeout", 5),
                            json={"command": command, **parameters},
                        )
                    else:
                        response = await client.get(
                            f"http://{self.ip}:{self.port}/{command}",
                            headers={"Token": self.jwt},
                            timeout=settings.get("api_function_timeout", 5),
                        )
                    json_data = response.json()
                    validation = self._validate_command_output(json_data)
                    if not validation[0]:
                        if i == settings.get("get_data_retries", 1):
                            raise APIError(validation[1])
                        # refresh the token, retry
                        await self.auth()
                        continue
                    return json_data
                except httpx.HTTPError:
                    pass
                except json.JSONDecodeError:
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

        data = {}
        for cmd in tasks:
            try:
                result = tasks[cmd].result()
                if result is None or result == {}:
                    result = {}
                data[cmd] = result
            except APIError:
                pass

        return data

    @staticmethod
    def _validate_command_output(data: dict) -> tuple:
        # check if the data returned is correct or an error
        # if status isn't a key, it is a multicommand
        if "STATUS" not in data.keys():
            for key in data.keys():
                # make sure not to try to turn id into a dict
                if not key == "id":
                    # make sure they succeeded
                    if "STATUS" in data[key][0].keys():
                        if data[key][0]["STATUS"][0]["STATUS"] not in ["S", "I"]:
                            # this is an error
                            return False, f"{key}: " + data[key][0]["STATUS"][0]["Msg"]
        elif "id" not in data.keys():
            if isinstance(data["STATUS"], list):
                if data["STATUS"][0].get("STATUS", None) in ["S", "I"]:
                    return True, None
                else:
                    return False, data["STATUS"][0]["Msg"]

            elif isinstance(data["STATUS"], dict):
                # new style X19 command
                if data["STATUS"]["STATUS"] not in ["S", "I"]:
                    return False, data["STATUS"]["Msg"]
                return True, None

            if data["STATUS"] not in ["S", "I"]:
                return False, data["Msg"]
        else:
            # make sure the command succeeded
            if isinstance(data["STATUS"], str):
                if data["STATUS"] in ["RESTART"]:
                    return True, None
            elif isinstance(data["STATUS"], dict):
                if data["STATUS"].get("STATUS") in ["S", "I"]:
                    return True, None
            elif data["STATUS"][0]["STATUS"] not in ("S", "I"):
                # this is an error
                if data["STATUS"][0]["STATUS"] not in ("S", "I"):
                    return False, data["STATUS"][0]["Msg"]
        return True, None

    async def factory_reset(self):
        return await self.send_command("factory-reset", post=True)

    async def get_fan(self):
        return await self.send_command("fan")

    async def set_fan(self, fan: int, speed_pct: int):
        return await self.send_command("fan", index=fan, percentage=speed_pct)

    async def firmware_upgrade(self, url: str = None, version: str = "latest"):
        if url is not None:
            return await self.send_command("firmware-upgrade", url=url)
        return await self.send_command("firmware-upgrade", version=version)

    async def get_frequency(self):
        return await self.send_command("frequency")

    async def set_frequency(self, board: int, frequency: float):
        return await self.send_command("frequency", board=board, frequency=frequency)

    async def ipreport(self):
        return await self.send_command("ipreport")

    async def get_led(self):
        return await self.send_command("led")

    async def set_led(self, code: int):
        return await self.send_command("led", code=code)

    async def set_led_custom(self, code: int, led_1: int, led_2: int, msg: str):
        return await self.send_command(
            "led", code=code, led1=led_1, led2=led_2, msg=msg
        )

    async def get_mode(self):
        return await self.send_command("mode")

    async def set_mode(self, **kwargs):
        return await self.send_command("mode", **kwargs)

    async def get_network(self):
        return await self.send_command("network")

    async def set_network(self, **kwargs):
        return await self.send_command("network", **kwargs)

    async def password(self, password: str):
        res = await self.send_command(
            "password", user=self.username, old=self.pwd, new=password
        )
        self.pwd = password
        return res

    async def get_psu(self):
        return await self.send_command("psu")

    async def set_psu(self, voltage: float):
        return await self.send_command("psu", voltage=voltage)

    async def get_register(self):
        return await self.send_command("register")

    async def set_register(self, company: str):
        return await self.send_command("register", parameter=company)

    async def reboot(self):
        return await self.send_command("restart", post=True)

    async def restart_gcminer(self):
        return await self.send_command("restart", parameter="gcminer")

    async def restart_api_server(self):
        return await self.send_command("restart", parameter="api-server")

    async def temperature(self):
        return await self.send_command("temperature")

    async def timedate(self, ntp: str, timezone: str):
        return await self.send_command("timedate", ntp=ntp, timezone=timezone)

    async def token(self):
        return await self.send_command("token", user=self.username, password=self.pwd)

    async def update_pools(self, pools: List[dict]):
        return await self.send_command("updatepools", pools=pools)

    async def voltage(self):
        return await self.send_command("voltage")

    async def get_ztp(self):
        return await self.send_command("ztp")

    async def set_ztp(self, enable: bool):
        return await self.send_command("ztp", parameter="on" if enable else "off")
