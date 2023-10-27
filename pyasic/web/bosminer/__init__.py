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
import json
import warnings
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Union

import grpc_requests
import httpx
from grpc import RpcError

from pyasic import APIError, settings
from pyasic.web import BaseWebAPI
from pyasic.web.bosminer.proto import (
    get_auth_service_descriptors,
    get_service_descriptors,
)


class SaveAction(Enum):
    UNSPECIFIED = "SaveAction.SAVE_ACTION_UNSPECIFIED"
    SAVE = "SaveAction.SAVE_ACTION_SAVE"
    SAVE_AND_APPLY = "SaveAction.SAVE_ACTION_SAVE_AND_APPLY"
    SAVE_AND_FORCE_APPLY = "SaveAction.SAVE_ACTION_SAVE_AND_FORCE_APPLY"


class BOSMinerWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        self.gql = BOSMinerGQLAPI(ip, settings.get("default_bosminer_password", "root"))
        self.luci = BOSMinerLuCIAPI(
            ip, settings.get("default_bosminer_password", "root")
        )
        self.grpc = BOSMinerGRPCAPI(
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
        self.gql.pwd = other

    async def send_command(
        self,
        command: Union[str, dict],
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Union[str, int, bool],
    ) -> dict:
        if isinstance(command, dict):
            return await self.gql.send_command(command)
        elif command.startswith("/cgi-bin/luci"):
            return await self.gql.send_command(command)

    async def multicommand(
        self, *commands: Union[dict, str], allow_warning: bool = True
    ) -> dict:
        luci_commands = []
        gql_commands = []
        for cmd in commands:
            if isinstance(cmd, dict):
                gql_commands.append(cmd)
            elif cmd.startswith("/cgi-bin/luci"):
                luci_commands.append(cmd)

        luci_data = await self.luci.multicommand(*luci_commands)
        gql_data = await self.gql.multicommand(*gql_commands)

        if gql_data is None:
            gql_data = {}
        if luci_data is None:
            luci_data = {}

        data = dict(**luci_data, **gql_data)
        return data


class BOSMinerGQLAPI:
    def __init__(self, ip: str, pwd: str):
        self.ip = ip
        self.username = "root"
        self.pwd = pwd

    async def multicommand(self, *commands: dict) -> dict:
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
                except (LookupError, ValueError):
                    pass
            if not data:
                data = {}
            data["multicommand"] = False
            return data

    async def send_command(
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


class BOSMinerLuCIAPI:
    def __init__(self, ip: str, pwd: str):
        self.ip = ip
        self.username = "root"
        self.pwd = pwd

    async def multicommand(self, *commands: str) -> dict:
        data = {}
        for command in commands:
            data[command] = await self.send_command(command, ignore_errors=True)
        return data

    async def send_command(self, path: str, ignore_errors: bool = False) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                await self.auth(client)
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

    async def auth(self, session: httpx.AsyncClient):
        login = {"luci_username": self.username, "luci_password": self.pwd}
        url = f"http://{self.ip}/cgi-bin/luci"
        headers = {
            "User-Agent": "BTC Tools v0.1",  # only seems to respond if this user-agent is set
            "Content-Type": "application/x-www-form-urlencoded",
        }
        await session.post(url, headers=headers, data=login)

    async def get_net_conf(self):
        return await self.send_command("/cgi-bin/luci/admin/network/iface_status/lan")

    async def get_cfg_metadata(self):
        return await self.send_command("/cgi-bin/luci/admin/miner/cfg_metadata")

    async def get_cfg_data(self):
        return await self.send_command("/cgi-bin/luci/admin/miner/cfg_data")

    async def get_bos_info(self):
        return await self.send_command("/cgi-bin/luci/bos/info")

    async def get_overview(self):
        return await self.send_command(
            "/cgi-bin/luci/admin/status/overview?status=1"
        )  # needs status=1 or it fails

    async def get_api_status(self):
        return await self.send_command("/cgi-bin/luci/admin/miner/api_status")


class BOSMinerGRPCAPI:
    def __init__(self, ip: str, pwd: str):
        self.ip = ip
        self.username = "root"
        self.pwd = pwd
        self._auth = None
        self._auth_time = datetime.now()

    @property
    def commands(self) -> list:
        return self.get_commands()

    def get_commands(self) -> list:
        return [
            func
            for func in
            # each function in self
            dir(self)
            if func
            not in ["send_command", "multicommand", "auth", "commands", "get_commands"]
            if callable(getattr(self, func)) and
            # no __ or _ methods
            not func.startswith("__") and not func.startswith("_")
        ]

    async def multicommand(self, *commands: str) -> dict:
        pass

    async def send_command(
        self, command: str, ignore_errors: bool = False, auth: bool = True, **parameters
    ) -> dict:
        service, method = command.split("/")
        metadata = []
        if auth:
            metadata.append(("authorization", await self.auth()))
        async with grpc_requests.StubAsyncClient(
            f"{self.ip}:50051", service_descriptors=get_service_descriptors()
        ) as client:
            await client.register_all_service()
            try:
                return await client.request(
                    service,
                    method,
                    request=parameters,
                    metadata=metadata,
                )
            except RpcError as e:
                if ignore_errors:
                    return {}
                raise APIError(e._details)

    async def auth(self):
        if self._auth is not None and self._auth_time - datetime.now() < timedelta(
            seconds=3540
        ):
            return self._auth
        await self._get_auth()
        return self._auth

    async def _get_auth(self):
        async with grpc_requests.StubAsyncClient(
            f"{self.ip}:50051", service_descriptors=get_auth_service_descriptors()
        ) as client:
            await client.register_all_service()
            method_meta = client.get_method_meta(
                "braiins.bos.v1.AuthenticationService", "Login"
            )
            _request = method_meta.method_type.request_parser(
                {"username": self.username, "password": self.pwd},
                method_meta.input_type,
            )
            metadata = await method_meta.handler(_request).initial_metadata()

            for key, value in metadata:
                if key == "authorization":
                    self._auth = value
                    self._auth_time = datetime.now()
                    return self._auth

    async def get_api_version(self):
        return await self.send_command(
            "braiins.bos.ApiVersionService/GetApiVersion", auth=False
        )

    async def start(self):
        return await self.send_command("braiins.bos.v1.ActionsService/Start")

    async def stop(self):
        return await self.send_command("braiins.bos.v1.ActionsService/Stop")

    async def pause_mining(self):
        return await self.send_command("braiins.bos.v1.ActionsService/PauseMining")

    async def resume_mining(self):
        return await self.send_command("braiins.bos.v1.ActionsService/ResumeMining")

    async def restart(self):
        return await self.send_command("braiins.bos.v1.ActionsService/Restart")

    async def reboot(self):
        return await self.send_command("braiins.bos.v1.ActionsService/Reboot")

    async def set_locate_device_status(self, enable: bool):
        return await self.send_command(
            "braiins.bos.v1.ActionsService/SetLocateDeviceStatus", enable=enable
        )

    async def get_locate_device_status(self):
        return await self.send_command(
            "braiins.bos.v1.ActionsService/GetLocateDeviceStatus"
        )

    async def set_password(self, password: str = None):
        kwargs = {}
        if password:
            kwargs["password"] = password
        return await self.send_command(
            "braiins.bos.v1.AuthenticationService/SetPassword", **kwargs
        )

    async def get_cooling_state(self):
        return await self.send_command("braiins.bos.v1.CoolingService/GetCoolingState")

    async def set_immersion_mode(
        self, enable: bool, save_action: SaveAction = SaveAction.SAVE_AND_APPLY
    ):
        return await self.send_command(
            "braiins.bos.v1.CoolingService/SetImmersionMode",
            save_action=save_action,
            enable_immersion_mode=enable,
        )

    async def get_tuner_state(self):
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/GetTunerState"
        )

    async def list_target_profiles(self):
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/ListTargetProfiles"
        )

    async def set_default_power_target(
        self, save_action: SaveAction = SaveAction.SAVE_AND_APPLY
    ):
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/SetDefaultPowerTarget",
            save_action=save_action,
        )

    async def set_power_target(
        self, power_target: int, save_action: SaveAction = SaveAction.SAVE_AND_APPLY
    ):
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/SetPowerTarget",
            save_action=save_action,
            power_target=power_target,
        )

    async def increment_power_target(
        self,
        power_target_increment: int,
        save_action: SaveAction = SaveAction.SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/IncrementPowerTarget",
            save_action=save_action,
            power_target_increment=power_target_increment,
        )

    async def decrement_power_target(
        self,
        power_target_decrement: int,
        save_action: SaveAction = SaveAction.SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/DecrementPowerTarget",
            save_action=save_action,
            power_target_decrement=power_target_decrement,
        )

    async def set_default_hashrate_target(
        self, save_action: SaveAction = SaveAction.SAVE_AND_APPLY
    ):
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/SetDefaultHashrateTarget",
            save_action=save_action,
        )

    async def set_hashrate_target(
        self, hashrate_target: int, save_action: SaveAction = SaveAction.SAVE_AND_APPLY
    ):
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/SetHashrateTarget",
            save_action=save_action,
            hashrate_target=hashrate_target,
        )

    async def increment_hashrate_target(
        self,
        hashrate_target_increment: int,
        save_action: SaveAction = SaveAction.SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/IncrementHashrateTarget",
            save_action=save_action,
            hashrate_target_increment=hashrate_target_increment,
        )

    async def decrement_hashrate_target(
        self,
        hashrate_target_decrement: int,
        save_action: SaveAction = SaveAction.SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/DecrementHashrateTarget",
            save_action=save_action,
            hashrate_target_decrement=hashrate_target_decrement,
        )

    async def set_dps(self):
        raise NotImplementedError
        return await self.send_command("braiins.bos.v1.PerformanceService/SetDPS")

    async def set_performance_mode(self):
        raise NotImplementedError
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/SetPerformanceMode"
        )

    async def get_active_performance_mode(self):
        return await self.send_command(
            "braiins.bos.v1.PerformanceService/GetActivePerformanceMode"
        )

    async def get_pool_groups(self):
        return await self.send_command("braiins.bos.v1.PoolService/GetPoolGroups")

    async def create_pool_group(self):
        raise NotImplementedError
        return await self.send_command("braiins.bos.v1.PoolService/CreatePoolGroup")

    async def update_pool_group(self):
        raise NotImplementedError
        return await self.send_command("braiins.bos.v1.PoolService/UpdatePoolGroup")

    async def remove_pool_group(self):
        raise NotImplementedError
        return await self.send_command("braiins.bos.v1.PoolService/RemovePoolGroup")

    async def get_miner_configuration(self):
        return await self.send_command(
            "braiins.bos.v1.ConfigurationService/GetMinerConfiguration"
        )

    async def get_constraints(self):
        return await self.send_command(
            "braiins.bos.v1.ConfigurationService/GetConstraints"
        )

    async def get_license_state(self):
        return await self.send_command("braiins.bos.v1.LicenseService/GetLicenseState")

    async def get_miner_status(self):
        return await self.send_command("braiins.bos.v1.MinerService/GetMinerStatus")

    async def get_miner_details(self):
        return await self.send_command("braiins.bos.v1.MinerService/GetMinerDetails")

    async def get_miner_stats(self):
        return await self.send_command("braiins.bos.v1.MinerService/GetMinerStats")

    async def get_hashboards(self):
        return await self.send_command("braiins.bos.v1.MinerService/GetHashboards")

    async def get_support_archive(self):
        return await self.send_command("braiins.bos.v1.MinerService/GetSupportArchive")

    async def enable_hashboards(
        self,
        hashboard_ids: List[str],
        save_action: SaveAction = SaveAction.SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "braiins.bos.v1.MinerService/EnableHashboards",
            hashboard_ids=hashboard_ids,
            save_action=save_action,
        )

    async def disable_hashboards(
        self,
        hashboard_ids: List[str],
        save_action: SaveAction = SaveAction.SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "braiins.bos.v1.MinerService/DisableHashboards",
            hashboard_ids=hashboard_ids,
            save_action=save_action,
        )
