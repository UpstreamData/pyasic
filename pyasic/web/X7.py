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
from typing import Union

import httpx

from pyasic.settings import PyasicSettings
from pyasic.web import BaseWebAPI


class X7WebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.pwd = PyasicSettings().global_x7_password

    async def send_command(
        self,
        command: Union[str, bytes],
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Union[str, int, bool],
    ) -> dict:
        url = f"http://{self.ip}/cgi-bin/{command}.cgi"
        auth = httpx.DigestAuth(self.username, self.pwd)
        try:
            async with httpx.AsyncClient() as client:
                if parameters:
                    data = await client.post(
                        url, data=json.dumps(parameters), auth=auth  # noqa
                    )
                else:
                    data = await client.get(url, auth=auth)
        except httpx.HTTPError:
            pass
        else:
            if data.status_code == 200:
                try:
                    return data.json()
                except json.decoder.JSONDecodeError:
                    pass

    async def get_miner_conf(self) -> dict:
        return await self.send_command("get_miner_conf")

    async def set_miner_conf(self, conf: dict) -> dict:
        return await self.send_command("set_miner_conf", **conf)

    async def blink(self, blink: bool) -> dict:
        if blink:
            return await self.send_command("blink", blink="true")
        return await self.send_command("blink", blink="false")

    async def reboot(self) -> dict:
        return await self.send_command("reboot")

    async def get_system_info(self) -> dict:
        return await self.send_command("get_system_info")

    async def get_network_info(self) -> dict:
        return await self.send_command("get_network_info")

    async def summary(self) -> dict:
        return await self.send_command("summary")

    async def get_blink_status(self) -> dict:
        return await self.send_command("get_blink_status")

    async def set_network_conf(
        self,
        ip: str,
        dns: str,
        gateway: str,
        subnet_mask: str,
        hostname: str,
        protocol: int,
    ) -> dict:
        return await self.send_command(
            "set_network_conf",
            ipAddress=ip,
            ipDns=dns,
            ipGateway=gateway,
            ipHost=hostname,
            ipPro=protocol,
            ipSub=subnet_mask,
        )
