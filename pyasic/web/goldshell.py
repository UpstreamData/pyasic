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

from pyasic.settings import PyasicSettings
from pyasic.web import BaseWebAPI


class GoldshellWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "admin"
        self.pwd = PyasicSettings().global_goldshell_password
        self.jwt = None

    async def auth(self):
        async with httpx.AsyncClient() as client:
            try:
                await client.get(f"http://{self.ip}/user/logout")
                auth = (
                    await client.get(
                        f"http://{self.ip}/user/login?username={self.username}&password={self.pwd}&cipher=false"
                    )
                ).json()
            except httpx.HTTPError:
                warnings.warn(f"Could not authenticate web token with miner: {self}")
            except json.JSONDecodeError:
                # try again with encrypted normal password
                try:
                    auth = (
                        await client.get(
                            f"http://{self.ip}/user/login?username=admin&password=bbad7537f4c8b6ea31eea0b3d760e257&cipher=true"
                        )
                    ).json()
                except (httpx.HTTPError, json.JSONDecodeError):
                    warnings.warn(
                        f"Could not authenticate web token with miner: {self}"
                    )
                else:
                    self.jwt = auth.get("JWT Token")
            else:
                self.jwt = auth.get("JWT Token")
            return self.jwt

    async def send_command(
        self,
        command: Union[str, bytes],
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Union[str, int, bool],
    ) -> dict:
        if parameters.get("pool_pwd"):
            parameters["pass"] = parameters["pool_pwd"]
            parameters.pop("pool_pwd")
        if not self.jwt:
            await self.auth()
        async with httpx.AsyncClient() as client:
            for i in range(PyasicSettings().miner_get_data_retries):
                try:
                    if parameters:
                        response = await client.put(
                            f"http://{self.ip}/mcb/{command}",
                            headers={"Authorization": "Bearer " + self.jwt},
                            timeout=5,
                            json=parameters,
                        )
                    else:
                        response = await client.get(
                            f"http://{self.ip}/mcb/{command}",
                            headers={"Authorization": "Bearer " + self.jwt},
                            timeout=5,
                        )
                    json_data = response.json()
                    return json_data
                except httpx.HTTPError:
                    pass
                except json.JSONDecodeError:
                    pass
                except TypeError:
                    await self.auth()

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        data = {k: None for k in commands}
        data["multicommand"] = True
        await self.auth()
        async with httpx.AsyncClient() as client:
            for command in commands:
                try:
                    response = await client.get(
                        f"http://{self.ip}/mcb/{command}",
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

    async def pools(self):
        return await self.send_command("pools")

    async def newpool(self, url: str, user: str, password: str):
        return await self.send_command("newpool", url=url, user=user, pool_pwd=password)

    async def delpool(self, url: str, user: str, password: str, dragid: int = 0):
        return await self.send_command(
            "delpool", url=url, user=user, pool_pwd=password, dragid=dragid
        )

    async def setting(self):
        return await self.send_command("setting")

    async def status(self):
        return await self.send_command("status")
