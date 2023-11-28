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

from pyasic import settings
from pyasic.web import BaseWebAPI
from pyasic.errors import APIError, APIWarning

class ePICWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "root"
        self.pwd = settings.get("default_epic_password", "letmein")
        self.token = None

    async def send_command(
            self,
            command: Union[str, bytes],
            ignore_errors: bool = False,
            allow_warning: bool = True,
            post: bool = False,
            **parameters: Union[str, int, bool],
    ) -> dict:
        if post or parameters != {}:
            post = True
        
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            for i in range(settings.get("get_data_retries", 1) + 1):
                try:
                    if post:
                        epic_param = {"param": parameters.get("parameters"),
                                      "password": self.pwd}
                        response = await client.post(
                            f"http://{self.ip}:4028/{command}",
                            timeout=5,
                            json=epic_param,
                        )
                    else:
                        response = await client.get(
                            f"http://{self.ip}:4028/{command}",
                            timeout=5,

                        )
                    if not response.status_code == 200:
                        continue
                    json_data = response.json()
                    if json_data:
                        # The API can return a fail status if the miner cannot return the requested data. Catch this and pass
                        if "result" in json_data and json_data["result"] is False and not post:
                            if not i > settings.get("get_data_retries", 1):
                                continue
                            if not ignore_errors:
                                raise APIError(json_data["error"])
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

    async def restart_epic(self) -> dict:
        return await self.send_command("softreboot", post=True, parameters=None)

    async def reboot(self) -> dict:
        return await self.send_command("reboot", post=True, parameters=None)

    async def pause_mining(self) -> dict:
        return await self.send_command("miner", post=True, parameters="Stop")

    async def resume_mining(self) -> dict:
        return await self.send_command("miner", post=True, parameters="Autostart")

    async def stop_mining(self) -> dict:
        return await self.send_command("miner", post=True, parameters="Stop")

    async def start_mining(self) -> dict:
        return await self.send_command("miner", post=True, parameters="Autostart")

    async def summary(self):
        return await self.send_command("summary")
    
    async def hashrate(self):
        return await self.send_command("hashrate")
    
    async def network(self):
        return await self.send_command("network")

    async def capabilities(self):
        return await self.send_command("capabilities")

