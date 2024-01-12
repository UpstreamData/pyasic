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
import logging
from datetime import timedelta

from betterproto import Message
from grpclib.client import Channel

from pyasic.errors import APIError

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


class BOSerGRPCAPI:
    def __init__(self, ip: str, pwd: str):
        self.ip = ip
        self.username = "root"
        self.pwd = pwd
        self.port = 50051
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
        result = {"multicommand": True}
        tasks = {}
        for command in commands:
            try:
                tasks[command] = asyncio.create_task(getattr(self, command)())
            except AttributeError:
                result["command"] = {}

        await asyncio.gather(*list(tasks.values()))

        for cmd in tasks:
            result[cmd] = tasks[cmd].result()

        return result

    async def send_command(
        self,
        command: str,
        message: Message = None,
        ignore_errors: bool = False,
        auth: bool = True,
    ) -> dict:
        metadata = []
        if auth:
            metadata.append(("authorization", await self.auth()))
        async with Channel(self.ip, self.port) as c:
            endpoint = getattr(BOSMinerGRPCStub(c), command)
            if endpoint is None:
                if not ignore_errors:
                    raise APIError(f"Command not found - {endpoint}")
                return {}
            return (await endpoint(message, metadata=metadata)).to_pydict()

    async def auth(self):
        if self._auth is not None and self._auth_time - datetime.now() < timedelta(
            seconds=3540
        ):
            return self._auth
        await self._get_auth()
        return self._auth

    async def _get_auth(self):
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
                    self._auth = auth
                    self._auth_time = datetime.now()
                    return self._auth

    async def get_api_version(self):
        return await self.send_command(
            "get_api_version", ApiVersionRequest(), auth=False
        )

    async def start(self):
        return await self.send_command("start", StartRequest())

    async def stop(self):
        return await self.send_command("stop", StopRequest())

    async def pause_mining(self):
        return await self.send_command("pause_mining", PauseMiningRequest())

    async def resume_mining(self):
        return await self.send_command("resume_mining", ResumeMiningRequest())

    async def restart(self):
        return await self.send_command("restart", RestartRequest())

    async def reboot(self):
        return await self.send_command("reboot", RebootRequest())

    async def set_locate_device_status(self, enable: bool):
        return await self.send_command(
            "set_locate_device_status", SetLocateDeviceStatusRequest(enable=enable)
        )

    async def get_locate_device_status(self):
        return await self.send_command(
            "get_locate_device_status", GetLocateDeviceStatusRequest()
        )

    async def set_password(self, password: str = None):
        return await self.send_command(
            "set_password", SetPasswordRequest(password=password)
        )

    async def get_cooling_state(self):
        return await self.send_command("get_cooling_state", GetCoolingStateRequest())

    async def set_immersion_mode(
        self,
        enable: bool,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "set_immersion_mode",
            SetImmersionModeRequest(
                enable_immersion_mode=enable, save_action=save_action
            ),
        )

    async def get_tuner_state(self):
        return await self.send_command("get_tuner_state", GetTunerStateRequest())

    async def list_target_profiles(self):
        return await self.send_command(
            "list_target_profiles", ListTargetProfilesRequest()
        )

    async def set_default_power_target(
        self, save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY
    ):
        return await self.send_command(
            "set_default_power_target",
            message=SetDefaultPowerTargetRequest(save_action=save_action),
        )

    async def set_power_target(
        self,
        power_target: int,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "set_power_target",
            SetPowerTargetRequest(
                power_target=Power(watt=power_target), save_action=save_action
            ),
        )

    async def increment_power_target(
        self,
        power_target_increment: int,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "increment_power_target",
            message=IncrementPowerTargetRequest(
                power_target_increment=Power(watt=power_target_increment),
                save_action=save_action,
            ),
        )

    async def decrement_power_target(
        self,
        power_target_decrement: int,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "decrement_power_target",
            message=DecrementPowerTargetRequest(
                power_target_decrement=Power(watt=power_target_decrement),
                save_action=save_action,
            ),
        )

    async def set_default_hashrate_target(
        self, save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY
    ):
        return await self.send_command(
            "set_default_hashrate_target",
            message=SetDefaultHashrateTargetRequest(save_action=save_action),
        )

    async def set_hashrate_target(
        self,
        hashrate_target: float,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "set_hashrate_target",
            SetHashrateTargetRequest(
                hashrate_target=TeraHashrate(terahash_per_second=hashrate_target),
                save_action=save_action,
            ),
        )

    async def increment_hashrate_target(
        self,
        hashrate_target_increment: int,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "increment_hashrate_target",
            IncrementHashrateTargetRequest(
                hashrate_target_increment=TeraHashrate(
                    terahash_per_second=hashrate_target_increment
                ),
                save_action=save_action,
            ),
        )

    async def decrement_hashrate_target(
        self,
        hashrate_target_decrement: int,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "decrement_hashrate_target",
            DecrementHashrateTargetRequest(
                hashrate_target_decrement=TeraHashrate(
                    terahash_per_second=hashrate_target_decrement
                ),
                save_action=save_action,
            ),
        )

    async def set_dps(
        self,
        enable: bool,
        power_step: int,
        min_power_target: int,
        enable_shutdown: bool = None,
        shutdown_duration: int = None,
    ):
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
        )

    async def set_performance_mode(
        self,
        wattage_target: int = None,
        hashrate_target: int = None,
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ):
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
            )

    async def get_active_performance_mode(self):
        return await self.send_command(
            "get_active_performance_mode", GetPerformanceModeRequest()
        )

    async def get_pool_groups(self):
        return await self.send_command("get_pool_groups", GetPoolGroupsRequest())

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
            "get_miner_configuration", GetMinerConfigurationRequest()
        )

    async def get_constraints(self):
        return await self.send_command("get_constraints", GetConstraintsRequest())

    async def get_license_state(self):
        return await self.send_command("get_license_state", GetLicenseStateRequest())

    async def get_miner_status(self):
        return await self.send_command("get_miner_status", GetMinerStatusRequest())

    async def get_miner_details(self):
        return await self.send_command("get_miner_details", GetMinerDetailsRequest())

    async def get_miner_stats(self):
        return await self.send_command("get_miner_stats", GetMinerStatsRequest())

    async def get_hashboards(self):
        return await self.send_command("get_hashboards", GetHashboardsRequest())

    async def get_support_archive(self):
        return await self.send_command(
            "get_support_archive", GetSupportArchiveRequest()
        )

    async def enable_hashboards(
        self,
        hashboard_ids: List[str],
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "enable_hashboards",
            EnableHashboardsRequest(
                hashboard_ids=hashboard_ids, save_action=save_action
            ),
        )

    async def disable_hashboards(
        self,
        hashboard_ids: List[str],
        save_action: SaveAction = SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
    ):
        return await self.send_command(
            "disable_hashboards",
            DisableHashboardsRequest(
                hashboard_ids=hashboard_ids, save_action=save_action
            ),
        )
