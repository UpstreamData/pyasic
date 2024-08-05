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

import aiofiles
import httpx
import json
from pathlib import Path
from typing import Any, Optional

from pyasic import settings
from pyasic.web.base import BaseWebAPI


class AvalonWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "admin"
        self.pwd = settings.get("default_avalon_web_password", "admin")
        self.port = 80
        self.token = None

    async def auth(self) -> None:
        """Authenticate and get the token. Implement the actual authentication logic here."""
        self.token = "Success"

    async def send_command(
        self,
        command: str | bytes,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        upgrade_file: Optional[Path] = None,
        **parameters: Any,
    ) -> dict:
        
        if self.token is None:
            await self.auth()

        async with httpx.AsyncClient(transport=settings.transport()) as client:
            for i in range(settings.get("get_data_retries", 1)):
                try:
                    if upgrade_file:
                        async with aiofiles.open(upgrade_file, "rb") as f:
                            upgrade_contents = await f.read()

                        url = f"http://{self.ip}:{self.port}/cgi-bin/upgrade"
                        data = {'version': parameters.get('version', 'latest')}
                        response = await client.post(
                            url,
                            files={'firmware': upgrade_contents},
                            data=data,
                            auth=(self.username, self.pwd),
                            timeout=60
                        )
                        return response.json()
                    else:
                        response = await client.get(
                            f"http://{self.ip}:{self.port}/{command}",
                            timeout=5,
                        )
                        return response.json()
                except (httpx.HTTPError, json.JSONDecodeError):
                    pass
        return {}

    async def update_firmware(self, ip: str, port: int, version: str = "latest", file: Optional[Path] = None) -> dict:
        """Perform a system update by uploading a firmware file and sending a
        command to initiate the update."""
        return await self.send_command(
            upgrade_file=file,
            version=version
        )