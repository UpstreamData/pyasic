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
from typing import Any

import httpx

from pyasic import settings
from pyasic.errors import APIError
from pyasic.web.base import BaseWebAPI


class ePICWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "root"
        self.pwd = settings.get("default_epic_web_password", "letmein")
        self.port = 4028
        self.token = None

    async def send_command(
        self,
        command: str | bytes,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        post = privileged or not parameters == {}

        async with httpx.AsyncClient(transport=settings.transport()) as client:
            for retry_cnt in range(settings.get("get_data_retries", 1)):
                try:
                    if post:
                        response = await client.post(
                            f"http://{self.ip}:{self.port}/{command}",
                            timeout=5,
                            json={
                                **parameters,
                                "password": self.pwd,
                            },
                        )
                    else:
                        response = await client.get(
                            f"http://{self.ip}:{self.port}/{command}",
                            timeout=5,
                        )
                    if not response.status_code == 200:
                        if not ignore_errors:
                            raise APIError(
                                f"Web command {command} failed with status code {response.status_code}"
                            )
                        return {}
                    json_data = response.json()
                    if json_data:
                        # The API can return a fail status if the miner cannot return the requested data. Catch this and pass
                        if not json_data.get("result", True) and not post:
                            if retry_cnt < settings.get("get_data_retries", 1) - 1:
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
        return await self.send_command("softreboot", privileged=True)

    async def reboot(self) -> dict:
        return await self.send_command("reboot", privileged=True)

    async def set_shutdown_temp(self, params: int) -> dict:
        return await self.send_command("shutdowntemp", param=params)

    async def set_critical_temp(self, params: int) -> dict:
        return await self.send_command("criticaltemp", param=params)

    async def set_fan(self, params: dict) -> dict:
        return await self.send_command("fanspeed", param=params)

    async def set_ptune_enable(self, params: bool) -> dict:
        return await self.send_command("perpetualtune", param=params)

    async def set_ptune_algo(self, params: dict) -> dict:
        return await self.send_command("perpetualtune/algo", param=params)

    async def set_pools(self, params: dict) -> dict:
        return await self.send_command("coin", param=params)

    async def pause_mining(self) -> dict:
        return await self.send_command("miner", param="Stop")

    async def resume_mining(self) -> dict:
        return await self.send_command("miner", param="Autostart")

    async def stop_mining(self) -> dict:
        return await self.send_command("miner", param="Stop")

    async def start_mining(self) -> dict:
        return await self.send_command("miner", param="Autostart")

    async def summary(self) -> dict:
        return await self.send_command("summary")

    async def hashrate(self) -> dict:
        return await self.send_command("hashrate")

    async def network(self) -> dict:
        return await self.send_command("network")

    async def capabilities(self) -> dict:
        return await self.send_command("capabilities")
