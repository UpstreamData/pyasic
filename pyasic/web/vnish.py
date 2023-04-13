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


class VNishWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "admin"
        self.pwd = PyasicSettings().global_vnish_password
        self.token = None

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
                self.token = json_auth["token"]
            return self.token

    async def send_command(
        self,
        command: Union[str, bytes],
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Union[str, int, bool],
    ) -> dict:
        if not self.token:
            await self.auth()
        async with httpx.AsyncClient() as client:
            for i in range(PyasicSettings().miner_get_data_retries):
                try:
                    auth = self.token
                    if command.startswith("system"):
                        auth = "Bearer " + self.token

                    if parameters.get("post"):
                        parameters.pop("post")
                        response = await client.post(
                            f"http://{self.ip}/api/v1/{command}",
                            headers={"Authorization": auth},
                            timeout=5,
                            json=parameters,
                        )
                    elif not parameters == {}:
                        response = await client.post(
                            f"http://{self.ip}/api/v1/{command}",
                            headers={"Authorization": auth},
                            timeout=5,
                            json=parameters,
                        )
                    else:
                        response = await client.get(
                            f"http://{self.ip}/api/v1/{command}",
                            headers={"Authorization": auth},
                            timeout=5,
                        )
                    if not response.status_code == 200:
                        # refresh the token, retry
                        await self.auth()
                        continue
                    json_data = response.json()
                    if json_data:
                        return json_data
                    return {"success": True}
                except httpx.HTTPError:
                    pass
                except json.JSONDecodeError:
                    pass
                except AttributeError:
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
        return await self.send_command("mining/restart", post=True)

    async def reboot(self) -> dict:
        return await self.send_command("system/reboot", post=True)

    async def info(self):
        return await self.send_command("info")

    async def summary(self):
        return await self.send_command("summary")
