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


class BOSMinerWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "root"
        self.pwd = settings.get("default_bosminer_password", "root")
        self.port = 80

    async def send_command(
        self,
        command: str | bytes,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        try:
            async with httpx.AsyncClient(transport=settings.transport()) as client:
                await self.auth(client)
                data = await client.get(
                    f"http://{self.ip}:{self.port}/cgi-bin/luci/{command}",
                    headers={"User-Agent": "BTC Tools v0.1"},
                )
                if data.status_code == 200:
                    return data.json()
                if ignore_errors:
                    return {}
                raise APIError(
                    f"LUCI web command failed: command={command}, code={data.status_code}"
                )
        except (httpx.HTTPError, json.JSONDecodeError):
            if ignore_errors:
                return {}
            raise APIError(f"LUCI web command failed: command={command}")

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        data = {}
        for command in commands:
            data[command] = await self.send_command(
                command, ignore_errors=ignore_errors
            )
        return data

    async def auth(self, session: httpx.AsyncClient) -> None:
        login = {"luci_username": self.username, "luci_password": self.pwd}
        url = f"http://{self.ip}:{self.port}/cgi-bin/luci"
        headers = {
            "User-Agent": (
                "BTC Tools v0.1"
            ),  # only seems to respond if this user-agent is set
            "Content-Type": "application/x-www-form-urlencoded",
        }
        await session.post(url, headers=headers, data=login)

    async def get_net_conf(self) -> dict:
        return await self.send_command("admin/network/iface_status/lan")

    async def get_cfg_metadata(self) -> dict:
        return await self.send_command("admin/miner/cfg_metadata")

    async def get_cfg_data(self) -> dict:
        return await self.send_command("admin/miner/cfg_data")

    async def get_bos_info(self) -> dict:
        return await self.send_command("bos/info")

    async def get_overview(self) -> dict:
        return await self.send_command(
            "admin/status/overview?status=1"
        )  # needs status=1 or it fails

    async def get_api_status(self) -> dict:
        return await self.send_command("admin/miner/api_status")
