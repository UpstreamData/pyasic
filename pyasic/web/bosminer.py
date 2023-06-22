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


class BOSMinerWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.pwd = PyasicSettings().global_bosminer_password

    def parse_command(self, graphql_command: Union[dict, set]) -> str:
        if isinstance(graphql_command, dict):
            data = []
            for key in graphql_command:
                if graphql_command[key] is not None:
                    parsed = self.parse_command(graphql_command[key])
                    data.append(key + parsed)
                else:
                    data.append(key)
        else:
            data = graphql_command
        return "{" + ",".join(data) + "}"

    async def send_command(
        self,
        command: dict,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Union[str, int, bool],
    ) -> dict:
        url = f"http://{self.ip}/graphql"
        query = self.parse_command(command)
        try:
            async with httpx.AsyncClient() as client:
                await self.auth(client)
                data = await client.post(url, json={"query": query})
        except httpx.HTTPError:
            pass
        else:
            if data.status_code == 200:
                try:
                    return data.json()
                except json.decoder.JSONDecodeError:
                    pass

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        def merge(*d: dict):
            ret = {}
            for i in d:
                if i:
                    for k in i:
                        if not k in ret:
                            ret[k] = i[k]
                        else:
                            ret[k] = merge(ret[k], i[k])
            return None if ret == {} else ret

        command = merge(*commands)
        data = await self.send_command(command)
        if data is not None:
            if data.get("data") is None:
                try:
                    commands = list(commands)
                    # noinspection PyTypeChecker
                    commands.remove({"bos": {"faultLight": None}})
                    command = merge(*commands)
                    data = await self.send_command(command)
                except LookupError:
                    pass
            if not data:
                data = {}
            data["multicommand"] = False
            return data

    async def auth(self, client: httpx.AsyncClient) -> None:
        url = f"http://{self.ip}/graphql"
        await client.post(
            url,
            json={
                "query": 'mutation{auth{login(username:"'
                + "root"
                + '", password:"'
                + self.pwd
                + '"){__typename}}}'
            },
        )
