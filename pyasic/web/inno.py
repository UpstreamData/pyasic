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
import warnings
from typing import Union

import httpx

from pyasic.errors import APIError
from pyasic.settings import PyasicSettings
from pyasic.web import BaseWebAPI


class InnosiliconWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "admin"
        self.pwd = PyasicSettings().global_innosilicon_password
        self.jwt = None

    async def auth(self):
        async with httpx.AsyncClient() as client:
            try:
                auth = await client.post(
                    f"http://{self.ip}/api/auth",
                    data={"username": self.username, "password": self.pwd},
                )
            except httpx.HTTPError:
                warnings.warn(f"Could not authenticate web token with miner: {self}")
            else:
                json_auth = auth.json()
                self.jwt = json_auth.get("jwt")
            return self.jwt

    async def send_command(
        self,
        command: Union[str, bytes],
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Union[str, int, bool],
    ) -> dict:
        if not self.jwt:
            await self.auth()
        async with httpx.AsyncClient() as client:
            for i in range(PyasicSettings().miner_get_data_retries):
                try:
                    response = await client.post(
                        f"http://{self.ip}/api/{command}",
                        headers={"Authorization": "Bearer " + self.jwt},
                        timeout=5,
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
                except httpx.HTTPError:
                    pass
                except json.JSONDecodeError:
                    pass

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        data = {k: None for k in commands}
        data["multicommand"] = True
        await self.auth()
        async with httpx.AsyncClient() as client:
            for command in commands:
                try:
                    response = await client.post(
                        f"http://{self.ip}/api/{command}",
                        headers={"Authorization": "Bearer " + self.jwt},
                        timeout=5,
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

    async def get_all(self):
        return await self.send_command("getAll")

    async def get_error_detail(self):
        return await self.send_command("getErrorDetail")

    async def pools(self):
        return await self.send_command("pools")

    async def poweroff(self):
        return await self.send_command("poweroff")
