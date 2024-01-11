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
import asyncio
from typing import Union

from pyasic import settings
from pyasic.errors import APIError
from pyasic.web import BaseWebAPI

from .graphql import BOSerGraphQLAPI
from .grpc import BOSerGRPCAPI
from .luci import BOSMinerLuCIAPI


class BOSMinerWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        self.luci = BOSMinerLuCIAPI(
            ip, settings.get("default_bosminer_password", "root")
        )
        self._pwd = settings.get("default_bosminer_password", "root")
        super().__init__(ip)

    @property
    def pwd(self):
        return self._pwd

    @pwd.setter
    def pwd(self, other: str):
        self._pwd = other
        self.luci.pwd = other

    async def send_command(
        self,
        command: Union[str, dict],
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Union[str, int, bool],
    ) -> dict:
        return await self.luci.send_command(command)

    async def multicommand(
        self, *commands: Union[dict, str], allow_warning: bool = True
    ) -> dict:
        return await self.luci.multicommand(*commands)


class BOSerWebAPI(BOSMinerWebAPI):
    def __init__(self, ip: str) -> None:
        self.gql = BOSerGraphQLAPI(
            ip, settings.get("default_bosminer_password", "root")
        )
        self.grpc = BOSerGRPCAPI(ip, settings.get("default_bosminer_password", "root"))
        super().__init__(ip)

    @property
    def pwd(self):
        return self._pwd

    @pwd.setter
    def pwd(self, other: str):
        self._pwd = other
        self.luci.pwd = other
        self.gql.pwd = other
        self.grpc.pwd = other

    async def send_command(
        self,
        command: Union[str, dict],
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Union[str, int, bool],
    ) -> dict:
        command_type = self.select_command_type(command)
        if command_type is "gql":
            return await self.gql.send_command(command)
        elif command_type is "grpc":
            try:
                return await (getattr(self.grpc, command.replace("grpc_", "")))()
            except AttributeError:
                raise APIError(f"No gRPC command found for command: {command}")
        elif command_type is "luci":
            return await self.luci.send_command(command)

    @staticmethod
    def select_command_type(command: Union[str, dict]) -> str:
        if isinstance(command, dict):
            return "gql"
        elif command.startswith("grpc_"):
            return "grpc"
        else:
            return "luci"

    async def multicommand(
        self, *commands: Union[dict, str], allow_warning: bool = True
    ) -> dict:
        cmd_types = {"grpc": [], "gql": [], "luci": []}
        for cmd in commands:
            cmd_types[self.select_command_type(cmd)] = cmd

        async def no_op():
            return {}

        if len(cmd_types["grpc"]) > 0:
            grpc_data_t = asyncio.create_task(
                self.grpc.multicommand(*cmd_types["grpc"])
            )
        else:
            grpc_data_t = no_op()
        if len(cmd_types["gql"]) > 0:
            gql_data_t = asyncio.create_task(self.gql.multicommand(*cmd_types["gql"]))
        else:
            gql_data_t = no_op()
        if len(cmd_types["luci"]) > 0:
            luci_data_t = asyncio.create_task(
                self.luci.multicommand(*cmd_types["luci"])
            )
        else:
            luci_data_t = no_op()

        await asyncio.gather(grpc_data_t, gql_data_t, luci_data_t)

        data = dict(
            **luci_data_t.result(), **gql_data_t.result(), **luci_data_t.result()
        )
        return data
