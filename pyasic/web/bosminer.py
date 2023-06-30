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

from pyasic import APIError
from pyasic.settings import PyasicSettings
from pyasic.web import BaseWebAPI


class BOSMinerWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.pwd = PyasicSettings().global_bosminer_password

    async def send_command(
        self,
        command: Union[str, dict],
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Union[str, int, bool],
    ) -> dict:
        if isinstance(command, str):
            return await self.send_luci_command(command)
        else:
            return await self.send_gql_command(command)

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

    async def send_gql_command(
        self,
        command: dict,
    ) -> dict:
        url = f"http://{self.ip}/graphql"
        query = command
        if command.get("query") is None:
            query = {"query": self.parse_command(command)}
        try:
            async with httpx.AsyncClient() as client:
                await self.auth(client)
                data = await client.post(url, json=query)
        except httpx.HTTPError:
            pass
        else:
            if data.status_code == 200:
                try:
                    return data.json()
                except json.decoder.JSONDecodeError:
                    pass

    async def multicommand(
        self, *commands: Union[dict, str], allow_warning: bool = True
    ) -> dict:
        luci_commands = []
        gql_commands = []
        for cmd in commands:
            if isinstance(cmd, dict):
                gql_commands.append(cmd)
            if isinstance(cmd, str):
                luci_commands.append(cmd)

        luci_data = await self.luci_multicommand(*luci_commands)
        gql_data = await self.gql_multicommand(*gql_commands)

        if gql_data is None:
            gql_data = {}
        if luci_data is None:
            luci_data = {}

        data = dict(**luci_data, **gql_data)
        return data

    async def luci_multicommand(self, *commands: str) -> dict:
        data = {}
        for command in commands:
            data[command] = await self.send_luci_command(command, ignore_errors=True)
        return data

    async def gql_multicommand(self, *commands: dict) -> dict:
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
                    data = await self.send_gql_command(command)
                except (LookupError, ValueError):
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

    async def send_luci_command(self, path: str, ignore_errors: bool = False) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                await self.luci_auth(client)
                data = await client.get(
                    f"http://{self.ip}{path}", headers={"User-Agent": "BTC Tools v0.1"}
                )
                if data.status_code == 200:
                    return data.json()
                if ignore_errors:
                    return {}
                raise APIError(
                    f"Web command failed: path={path}, code={data.status_code}"
                )
        except (httpx.HTTPError, json.JSONDecodeError):
            if ignore_errors:
                return {}
            raise APIError(f"Web command failed: path={path}")

    async def luci_auth(self, session: httpx.AsyncClient):
        login = {"luci_username": self.username, "luci_password": self.pwd}
        url = f"http://{self.ip}/cgi-bin/luci"
        headers = {
            "User-Agent": "BTC Tools v0.1",  # only seems to respond if this user-agent is set
            "Content-Type": "application/x-www-form-urlencoded",
        }
        await session.post(url, headers=headers, data=login)

    async def get_net_conf(self):
        return await self.send_luci_command(
            "/cgi-bin/luci/admin/network/iface_status/lan"
        )

    async def get_cfg_metadata(self):
        return await self.send_luci_command("/cgi-bin/luci/admin/miner/cfg_metadata")

    async def get_cfg_data(self):
        return await self.send_luci_command("/cgi-bin/luci/admin/miner/cfg_data")

    async def get_bos_info(self):
        return await self.send_luci_command("/cgi-bin/luci/bos/info")

    async def get_overview(self):
        return await self.send_luci_command(
            "/cgi-bin/luci/admin/status/overview?status=1"
        )  # needs status=1 or it fails

    async def get_api_status(self):
        return await self.send_luci_command("/cgi-bin/luci/admin/miner/api_status")
