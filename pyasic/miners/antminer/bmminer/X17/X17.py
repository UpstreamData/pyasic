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
from typing import Optional, Union

import httpx

from pyasic.miners._backends import BMMiner  # noqa - Ignore access to _module
from pyasic.settings import PyasicSettings


class BMMinerX17(BMMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        self.ip = ip
        self.uname = "root"
        self.pwd = PyasicSettings().global_x17_password

    async def send_web_command(
        self, command: str, params: dict = None
    ) -> Optional[dict]:
        url = f"http://{self.ip}/cgi-bin/{command}.cgi"
        auth = httpx.DigestAuth(self.uname, self.pwd)
        try:
            async with httpx.AsyncClient() as client:
                if params:
                    data = await client.post(url, data=params, auth=auth)
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

    async def get_mac(self) -> Union[str, None]:
        try:
            data = await self.send_web_command("get_system_info")
            if data:
                return data["macaddr"]
        except KeyError:
            pass

    async def fault_light_on(self) -> bool:
        # this should time out, after it does do a check
        await self.send_web_command("blink", params={"action": "startBlink"})
        try:
            data = await self.send_web_command(
                "blink", params={"action": "onPageLoaded"}
            )
            if data:
                if data["isBlinking"]:
                    self.light = True
        except KeyError:
            pass
        return self.light

    async def fault_light_off(self) -> bool:
        await self.send_web_command("blink", params={"action": "stopBlink"})
        try:
            data = await self.send_web_command(
                "blink", params={"action": "onPageLoaded"}
            )
            if data:
                if not data["isBlinking"]:
                    self.light = False
        except KeyError:
            pass
        return self.light

    async def reboot(self) -> bool:
        data = await self.send_web_command("reboot")
        if data:
            return True
        return False

    async def get_fault_light(self) -> bool:
        if self.light:
            return self.light
        try:
            data = await self.send_web_command(
                "blink", params={"action": "onPageLoaded"}
            )
            if data:
                self.light = data["isBlinking"]
        except KeyError:
            pass
        return self.light

    async def get_hostname(self) -> Union[str, None]:
        try:
            data = await self.send_web_command("get_system_info")
            if data:
                return data["hostname"]
        except KeyError:
            pass
