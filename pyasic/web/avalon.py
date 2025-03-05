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
from typing import Any

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
        command: str,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        if self.token is None:
            await self.auth()

        async with httpx.AsyncClient(transport=settings.transport()) as client:
            try:
                url = f"http://{self.ip}:{self.port}/{command}"
                
                if 'file' in parameters:
                    file = parameters.pop('file')
                    async with aiofiles.open(file, "rb") as f:
                        file_contents = await f.read()
                    files = {'firmware': file_contents}
                    response = await client.post(
                        url,
                        files=files,
                        data=parameters,
                        auth=(self.username, self.pwd),
                        timeout=60
                    )
                else:
                    response = await client.get(
                        url,
                        params=parameters,
                        auth=(self.username, self.pwd),
                        timeout=5,
                    )

                return response.json()
            except (httpx.HTTPError, json.JSONDecodeError):
                if not ignore_errors:
                    raise
        return {}

    async def update_firmware(self, file: Path) -> dict:
        """Perform a system update by uploading a firmware file and sending a command to initiate the update."""
        return await self.send_command(
            command="cgi-bin/upgrade",
            file=file,
        )