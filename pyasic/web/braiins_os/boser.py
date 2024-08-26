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

import asyncio
import logging
from datetime import timedelta
from typing import Any

from grpclib import GRPCError, Status
from grpclib.client import Channel

from pyasic import settings
from pyasic.errors import APIError
from pyasic.web.base import BaseWebAPI

from .proto.braiins.bos import *
from .proto.braiins.bos.v1 import *


class BOSMinerGRPCStub(
    ApiVersionServiceStub,
    AuthenticationServiceStub,
    CoolingServiceStub,
    ConfigurationServiceStub,
    MinerServiceStub,
    PoolServiceStub,
    LicenseServiceStub,
    ActionsServiceStub,
    PerformanceServiceStub,
):
    pass


class BOSerWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username = "root"
        self.pwd = settings.get("default_bosminer_password", "root")
        self.port = 50051
        self._auth_time = None

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

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        result = {"multicommand": True}
        tasks = {}
        for command in commands:
            try:
                tasks[command] = asyncio.create_task(getattr(self, command)())
            except AttributeError:
                pass

        await asyncio.gather(*[t for t in tasks.values()], return_exceptions=True)

        for cmd in tasks:
            try:
                result[cmd] = await tasks[cmd]
            except (GRPCError, APIError):
                pass

        return result

    async def send_command(
        self,
        command: str | bytes,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        message: betterproto.Message = parameters["message"]
        metadata = []
        if privileged:
            metadata.append(("authorization", await self.auth()))
        try:
            async with Channel(self.ip, self.port) as c:
                endpoint = getattr(BOSMinerGRPCStub(c), command)
                if endpoint is None:
                    if not ignore_errors:
                        raise APIError(f"Command not found - {endpoint}")
                    return {}
                try:
                    return (await endpoint(message, metadata=metadata)).to_pydict()
                except GRPCError as e:
                    if e.status == Status.UNAUTHENTICATED:
                        await self._get_auth()
                        metadata = [("authorization", await self.auth())]
                        return (await endpoint(message, metadata=metadata)).to_pydict()
                    raise e
        except GRPCError as e:
            raise APIError(f"gRPC command failed - {endpoint}") from e

    async def auth(self) -> str | None:
        if self.token is not None and self._auth_time - datetime.now() < timedelta(
            seconds=3540
        ):
            return self.token
        await self._get_auth()
        return self.token

    async def _get_auth(self) -> str:
        async with Channel(self.ip, self.port) as c:
            req = LoginRequest(username=self.username, password=self.pwd)
            async with c.request(
                "/braiins.bos.v1.AuthenticationService/Login",
                grpclib.const.Cardinality.UNARY_UNARY,
                type(req),
                LoginResponse,
            ) as stream:
                await stream.send_message(req, end=True)
                await stream.recv_initial_metadata()
                auth = stream.initial_metadata.get("authorization")
                if auth is not None:
                    self.token = auth
                    self._auth_time = datetime.now()
                    return self.token

    async def get_api_version(self) -> dict:
        return await self.send_command(
            "get_api_version", message=ApiVersionRequest(), privileged=False
        )

    async def start(self) -> dict:
        return await self.send_command("start", message=StartRequest(), privileged=True)

    async def stop(self) -> dict:
        return await self.send_command("stop", message=StopRequest(), privileged=True)

    async def pause_mining(self) -> dict:
        return await self.send_command(
            "pause_mining", message=PauseMiningRequest(), privileged=True
        )

    async def resume_mining(self) -> dict:
        return await self.send_command(
            "resume_mining", message=ResumeMiningRequest(), privileged=True
        )

    async def restart(self) -> dict:
        return await self.send_command(
            "restart", message=RestartRequest(), privileged=True
        )

    async def reboot(self) -> dict:
        return await self.send_command(
            "reboot", message=RebootRequest(), privileged=True
        )

    async def set_locate_device_status(self, enable: bool) -> dict:
        return await self.send_command(
            "set_locate_device_status",
            message=SetLocateDeviceStatusRequest(enable=enable),
            privileged=True,
        )

    async def get_locate_device_status(self) -> dict:
        return await self.send_command(
            "get_locate_device_status",
            message=GetLocateDeviceStatusRequest(),
            privileged=True,
        )

    async def set_password(self, password: str = None) -> dict:
        return await self.send_command(
            "set_password",
            message=SetPasswordRequest(password=password),
            privileged=True,
        )

    async def get_cooling_state(self) -> dict:
        return await self.send_command(
            "get_cooling_state", message=GetCoolingStateRequest(), privileged=True
        )

    async def set_immersion_mode(
        self,
        enable: bool,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ) -> dict:
        return await self.send_command(
            "set_immersion_mode",
            message=SetImmersionModeRequest(
                enable_immersion_mode=enable, save_action=save_action
            ),
            privileged=True,
        )

    async def get_tuner_state(self) -> dict:
        return await self.send_command(
            "get_tuner_state", message=GetTunerStateRequest(), privileged=True
        )

    async def list_target_profiles(self) -> dict:
        return await self.send_command(
            "list_target_profiles", message=ListTargetProfilesRequest(), privileged=True
        )

    async def set_default_power_target(
        self, save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY
    ) -> dict:
        return await self.send_command(
            "set_default_power_target",
            message=SetDefaultPowerTargetRequest(save_action=save_action),
            privileged=True,
        )

    async def set_power_target(
        self,
        power_target: int,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ) -> dict:
        return await self.send_command(
            "set_power_target",
            message=SetPowerTargetRequest(
                power_target=Power(watt=power_target), save_action=save_action
            ),
            privileged=True,
        )

    async def increment_power_target(
        self,
        power_target_increment: int,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ) -> dict:
        return await self.send_command(
            "increment_power_target",
            message=IncrementPowerTargetRequest(
                power_target_increment=Power(watt=power_target_increment),
                save_action=save_action,
            ),
            privileged=True,
        )

    async def decrement_power_target(
        self,
        power_target_decrement: int,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ) -> dict:
        return await self.send_command(
            "decrement_power_target",
            message=DecrementPowerTargetRequest(
                power_target_decrement=Power(watt=power_target_decrement),
                save_action=save_action,
            ),
            privileged=True,
        )

    async def set_default_hashrate_target(
        self, save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY
    ) -> dict:
        return await self.send_command(
            "set_default_hashrate_target",
            message=SetDefaultHashrateTargetRequest(save_action=save_action),
            privileged=True,
        )

    async def set_hashrate_target(
        self,
        hashrate_target: float,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ) -> dict:
        return await self.send_command(
            "set_hashrate_target",
            message=SetHashrateTargetRequest(
                hashrate_target=TeraHashrate(terahash_per_second=hashrate_target),
                save_action=save_action,
            ),
            privileged=True,
        )

    async def increment_hashrate_target(
        self,
        hashrate_target_increment: int,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ) -> dict:
        return await self.send_command(
            "increment_hashrate_target",
            message=IncrementHashrateTargetRequest(
                hashrate_target_increment=TeraHashrate(
                    terahash_per_second=hashrate_target_increment
                ),
                save_action=save_action,
            ),
            privileged=True,
        )

    async def decrement_hashrate_target(
        self,
        hashrate_target_decrement: int,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ) -> dict:
        return await self.send_command(
            "decrement_hashrate_target",
            message=DecrementHashrateTargetRequest(
                hashrate_target_decrement=TeraHashrate(
                    terahash_per_second=hashrate_target_decrement
                ),
                save_action=save_action,
            ),
            privileged=True,
        )

    async def set_dps(
        self,
        enable: bool,
        power_step: int,
        min_power_target: int,
        enable_shutdown: bool = None,
        shutdown_duration: int = None,
    ) -> dict:
        return await self.send_command(
            "set_dps",
            message=SetDpsRequest(
                enable=enable,
                enable_shutdown=enable_shutdown,
                shutdown_duration=shutdown_duration,
                target=DpsTarget(
                    power_target=DpsPowerTarget(
                        power_step=Power(power_step),
                        min_power_target=Power(min_power_target),
                    )
                ),
            ),
            privileged=True,
        )

    async def set_performance_mode(
        self,
        wattage_target: int = None,
        hashrate_target: int = None,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ) -> dict:
        if wattage_target is not None and hashrate_target is not None:
            logging.error(
                "Cannot use both wattage_target and hashrate_target, using wattage_target."
            )
        elif wattage_target is None and hashrate_target is None:
            raise APIError(
                "No target supplied, please supply either wattage_target or hashrate_target."
            )
        if wattage_target is not None:
            return await self.send_command(
                "set_performance_mode",
                message=SetPerformanceModeRequest(
                    save_action=save_action,
                    mode=PerformanceMode(
                        tuner_mode=TunerPerformanceMode(
                            power_target=PowerTargetMode(
                                power_target=Power(watt=wattage_target)
                            )
                        )
                    ),
                ),
                privileged=True,
            )
        if hashrate_target is not None:
            return await self.send_command(
                "set_performance_mode",
                message=SetPerformanceModeRequest(
                    save_action=save_action,
                    mode=PerformanceMode(
                        tuner_mode=TunerPerformanceMode(
                            hashrate_target=HashrateTargetMode(
                                hashrate_target=TeraHashrate(
                                    terahash_per_second=hashrate_target
                                )
                            )
                        )
                    ),
                ),
                privileged=True,
            )

    async def get_active_performance_mode(self) -> dict:
        return await self.send_command(
            "get_active_performance_mode",
            message=GetPerformanceModeRequest(),
            privileged=True,
        )

    async def get_pool_groups(self) -> dict:
        return await self.send_command(
            "get_pool_groups", message=GetPoolGroupsRequest(), privileged=True
        )

    async def get_miner_configuration(self) -> dict:
        return await self.send_command(
            "get_miner_configuration",
            message=GetMinerConfigurationRequest(),
            privileged=True,
        )

    async def get_constraints(self) -> dict:
        return await self.send_command(
            "get_constraints", message=GetConstraintsRequest(), privileged=True
        )

    async def get_license_state(self) -> dict:
        return await self.send_command(
            "get_license_state", message=GetLicenseStateRequest(), privileged=True
        )

    async def get_miner_status(self) -> dict:
        return await self.send_command(
            "get_miner_status", message=GetMinerStatusRequest(), privileged=True
        )

    async def get_miner_details(self) -> dict:
        return await self.send_command(
            "get_miner_details", message=GetMinerDetailsRequest(), privileged=True
        )

    async def get_miner_stats(self) -> dict:
        return await self.send_command(
            "get_miner_stats", message=GetMinerStatsRequest(), privileged=True
        )

    async def get_hashboards(self) -> dict:
        return await self.send_command(
            "get_hashboards", message=GetHashboardsRequest(), privileged=True
        )

    async def get_support_archive(self) -> dict:
        return await self.send_command(
            "get_support_archive", message=GetSupportArchiveRequest(), privileged=True
        )

    async def enable_hashboards(
        self,
        hashboard_ids: List[str],
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ) -> dict:
        return await self.send_command(
            "enable_hashboards",
            message=EnableHashboardsRequest(
                hashboard_ids=hashboard_ids, save_action=save_action
            ),
            privileged=True,
        )

    async def disable_hashboards(
        self,
        hashboard_ids: List[str],
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ) -> dict:
        return await self.send_command(
            "disable_hashboards",
            message=DisableHashboardsRequest(
                hashboard_ids=hashboard_ids, save_action=save_action
            ),
            privileged=True,
        )

    async def set_pool_groups(
        self,
        pool_groups: List[PoolGroupConfiguration],
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ) -> dict:
        return await self.send_command(
            "set_pool_groups",
            message=SetPoolGroupsRequest(
                save_action=save_action, pool_groups=pool_groups
            ),
        )
