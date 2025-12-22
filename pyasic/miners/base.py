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
import ipaddress
import warnings
from typing import Any, Protocol, TypeVar

from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard, MinerData
from pyasic.data.device import DeviceInfo
from pyasic.data.error_codes import MinerErrorData
from pyasic.data.pools import PoolMetrics
from pyasic.device.algorithm import AlgoHashRateType, MinerAlgoType
from pyasic.device.algorithm.base import GenericAlgo
from pyasic.device.firmware import MinerFirmware
from pyasic.device.makes import MinerMake
from pyasic.device.models import MinerModelType
from pyasic.errors import APIError
from pyasic.logger import logger
from pyasic.miners.data import DataOptions, RPCAPICommand, WebAPICommand


class MinerProtocol(Protocol):
    _rpc_cls: type[Any] | None = None
    _web_cls: type[Any] | None = None
    _ssh_cls: type[Any] | None = None

    ip: str | None = None
    rpc: Any | None = None
    web: Any | None = None
    ssh: Any | None = None

    make: MinerMake | None = None
    raw_model: MinerModelType | None = None
    firmware: MinerFirmware | None = None
    algo: type[MinerAlgoType] = GenericAlgo

    expected_hashboards: int | None = None
    expected_chips: int | None = None
    expected_fans: int | None = None

    data_locations: Any | None = None

    supports_shutdown: bool = False
    supports_power_modes: bool = False
    supports_presets: bool = False
    supports_autotuning: bool = False

    api_ver: str | None = None
    fw_ver: str | None = None
    light: bool | None = None
    config: MinerConfig | None = None

    def __repr__(self):
        return f"{self.model}: {str(self.ip)}"

    def __lt__(self, other):
        return ipaddress.ip_address(self.ip) < ipaddress.ip_address(other.ip)

    def __gt__(self, other):
        return ipaddress.ip_address(self.ip) > ipaddress.ip_address(other.ip)

    def __eq__(self, other):
        return ipaddress.ip_address(self.ip) == ipaddress.ip_address(other.ip)

    @property
    def model(self) -> str:
        if self.raw_model is not None:
            model_data = [str(self.raw_model)]
        elif self.make is not None:
            model_data = [str(self.make)]
        else:
            model_data = ["Unknown"]
        if self.firmware is not None:
            model_data.append(f"({self.firmware})")
        return " ".join(model_data)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            make=self.make, model=self.raw_model, firmware=self.firmware, algo=self.algo
        )

    @property
    def api(self):
        return self.rpc

    async def check_light(self) -> bool:
        """Get the status of the fault light as a boolean.

        Returns:
            A boolean value representing the fault light status.
        """
        return await self.get_fault_light()

    async def fault_light_on(self) -> bool:
        """Turn the fault light of the miner on and return success as a boolean.

        Returns:
            A boolean value of the success of turning the light on.
        """
        return False

    async def fault_light_off(self) -> bool:
        """Turn the fault light of the miner off and return success as a boolean.

        Returns:
            A boolean value of the success of turning the light off.
        """
        return False

    async def get_config(self) -> MinerConfig:
        # Not a data gathering function, since this is used for configuration
        """Get the mining configuration of the miner and return it as a [`MinerConfig`][pyasic.config.MinerConfig].

        Returns:
            A [`MinerConfig`][pyasic.config.MinerConfig] containing the pool information and mining configuration.
        """
        return MinerConfig()

    async def reboot(self) -> bool:
        """Reboot the miner and return success as a boolean.

        Returns:
            A boolean value of the success of rebooting the miner.
        """
        return False

    async def restart_backend(self) -> bool:
        """Restart the mining process of the miner (bosminer, bmminer, cgminer, etc) and return success as a boolean.

        Returns:
            A boolean value of the success of restarting the mining process.
        """
        return False

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        """Set the mining configuration of the miner.

        Parameters:
            config: A [`MinerConfig`][pyasic.config.MinerConfig] containing the mining config you want to switch the miner to.
            user_suffix: A suffix to append to the username when sending to the miner.
        """
        return None

    async def stop_mining(self) -> bool:
        """Stop the mining process of the miner.

        Returns:
            A boolean value of the success of stopping the mining process.
        """
        return False

    async def resume_mining(self) -> bool:
        """Resume the mining process of the miner.

        Returns:
            A boolean value of the success of resuming the mining process.
        """
        return False

    async def set_power_limit(self, wattage: int) -> bool:
        """Set the power limit to be used by the miner.

        Parameters:
            wattage: The power limit to set on the miner.

        Returns:
            A boolean value of the success of setting the power limit.
        """
        return False

    async def upgrade_firmware(
        self,
        *,
        file: str | None = None,
        url: str | None = None,
        version: str | None = None,
        keep_settings: bool = True,
    ) -> bool:
        """Upgrade the firmware of the miner.

        Parameters:
            file: The file path to the firmware to upgrade from. Must be a valid file path if provided.
            url: The URL to download the firmware from. Must be a valid URL if provided.
            version: The version of the firmware to upgrade to. If None, the version will be inferred from the file or URL.
            keep_settings: Whether to keep the current settings during the upgrade. Defaults to True.

        Returns:
            A boolean value of the success of the firmware upgrade.
        """
        return False

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_serial_number(self) -> str | None:
        """Get the serial number of the miner and return it as a string.

        Returns:
            A string representing the serial number of the miner.
        """
        return await self._get_serial_number()

    async def get_psu_serial_number(self) -> str | None:
        """Get the PSU serial number reported by the miner.

        Returns:
            A string representing the PSU serial number of the miner.
        """
        return await self._get_psu_serial_number()

    async def get_mac(self) -> str | None:
        """Get the MAC address of the miner and return it as a string.

        Returns:
            A string representing the MAC address of the miner.
        """
        return await self._get_mac()

    async def get_model(self) -> str | None:
        """Get the model of the miner and return it as a string.

        Returns:
            A string representing the model of the miner.
        """
        return self.model

    async def get_device_info(self) -> DeviceInfo | None:
        """Get device information, including model, make, and firmware.

        Returns:
            A dataclass containing device information.
        """
        return self.device_info

    async def get_api_ver(self) -> str | None:
        """Get the API version of the miner and is as a string.

        Returns:
            API version as a string.
        """
        return await self._get_api_ver()

    async def get_fw_ver(self) -> str | None:
        """Get the firmware version of the miner and is as a string.

        Returns:
            Firmware version as a string.
        """
        return await self._get_fw_ver()

    async def get_version(self) -> tuple[str | None, str | None]:
        """Get the API version and firmware version of the miner and return them as strings.

        Returns:
            A tuple of (API version, firmware version) as strings.
        """
        api_ver = await self.get_api_ver()
        fw_ver = await self.get_fw_ver()
        return api_ver, fw_ver

    async def get_hostname(self) -> str | None:
        """Get the hostname of the miner and return it as a string.

        Returns:
            A string representing the hostname of the miner.
        """
        return await self._get_hostname()

    async def get_hashrate(self) -> AlgoHashRateType | None:
        """Get the hashrate of the miner and return it as a float in TH/s.

        Returns:
            Hashrate of the miner in TH/s as a float.
        """
        return await self._get_hashrate()

    async def get_hashboards(self) -> list[HashBoard]:
        """Get hashboard data from the miner in the form of [`HashBoard`][pyasic.data.HashBoard].

        Returns:
            A [`HashBoard`][pyasic.data.HashBoard] instance containing hashboard data from the miner.
        """
        return await self._get_hashboards()

    async def get_env_temp(self) -> float | None:
        """Get environment temp from the miner as a float.

        Returns:
            Environment temp of the miner as a float.
        """
        return await self._get_env_temp()

    async def get_wattage(self) -> int | None:
        """Get wattage from the miner as an int.

        Returns:
            Wattage of the miner as an int.
        """
        return await self._get_wattage()

    async def get_voltage(self) -> float | None:
        """Get output voltage of the PSU as a float.

        Returns:
            Output voltage of the PSU as an float.
        """
        return await self._get_voltage()

    async def get_wattage_limit(self) -> int | None:
        """Get wattage limit from the miner as an int.

        Returns:
            Wattage limit of the miner as an int.
        """
        return await self._get_wattage_limit()

    async def get_fans(self) -> list[Fan]:
        """Get fan data from the miner in the form [fan_1, fan_2, fan_3, fan_4].

        Returns:
            A list of fan data.
        """
        return await self._get_fans()

    async def get_fan_psu(self) -> int | None:
        """Get PSU fan speed from the miner.

        Returns:
            PSU fan speed.
        """
        return await self._get_fan_psu()

    async def get_errors(self) -> list[MinerErrorData]:
        """Get a list of the errors the miner is experiencing.

        Returns:
            A list of error classes representing different errors.
        """
        return await self._get_errors()

    async def get_fault_light(self) -> bool:
        """Check the status of the fault light and return on or off as a boolean.

        Returns:
            A boolean value where `True` represents on and `False` represents off.
        """
        result = await self._get_fault_light()
        return result if result is not None else False

    async def get_expected_hashrate(self) -> AlgoHashRateType | None:
        """Get the nominal hashrate from factory if available.

        Returns:
            A float value of nominal hashrate in TH/s.
        """
        return await self._get_expected_hashrate()

    async def is_mining(self) -> bool | None:
        """Check whether the miner is mining.

        Returns:
            A boolean value representing if the miner is mining.
        """
        return await self._is_mining()

    async def get_uptime(self) -> int | None:
        """Get the uptime of the miner in seconds.

        Returns:
            The uptime of the miner in seconds.
        """
        return await self._get_uptime()

    async def get_pools(self) -> list[PoolMetrics]:
        """Get the pools information from Miner.

        Returns:
            The pool information of the miner.
        """
        return await self._get_pools()

    async def _get_serial_number(self) -> str | None:
        pass

    async def _get_psu_serial_number(self) -> str | None:
        return None

    async def _get_mac(self) -> str | None:
        return None

    async def _get_api_ver(self) -> str | None:
        return None

    async def _get_fw_ver(self) -> str | None:
        return None

    async def _get_hostname(self) -> str | None:
        return None

    async def _get_hashrate(self) -> AlgoHashRateType | None:
        return None

    async def _get_hashboards(self) -> list[HashBoard]:
        return []

    async def _get_env_temp(self) -> float | None:
        return None

    async def _get_wattage(self) -> int | None:
        return None

    async def _get_voltage(self) -> float | None:
        return None

    async def _get_wattage_limit(self) -> int | None:
        return None

    async def _get_fans(self) -> list[Fan]:
        return []

    async def _get_fan_psu(self) -> int | None:
        return None

    async def _get_errors(self) -> list[MinerErrorData]:
        return []

    async def _get_fault_light(self) -> bool | None:
        return None

    async def _get_expected_hashrate(self) -> AlgoHashRateType | None:
        return None

    async def _is_mining(self) -> bool | None:
        return None

    async def _get_uptime(self) -> int | None:
        return None

    async def _get_pools(self) -> list[PoolMetrics]:
        return []

    async def _get_data(
        self,
        allow_warning: bool,
        include: list[str | DataOptions] | None = None,
        exclude: list[str | DataOptions] | None = None,
    ) -> dict:
        # handle include
        if include is not None:
            include = [str(i) for i in include]
        else:
            # everything
            include = [str(enum_value.value) for enum_value in DataOptions]

        # handle exclude
        # prioritized over include, including x and excluding x will exclude x
        if exclude is not None:
            for item in exclude:
                if str(item) in include:
                    include.remove(str(item))

        rpc_multicommand = set()
        web_multicommand = set()
        # create multicommand
        for data_name in include:
            try:
                # get kwargs needed for the _get_xyz function
                fn_args = getattr(self.data_locations, str(data_name)).kwargs

                # keep track of which RPC/Web commands need to be sent
                for arg in fn_args:
                    if isinstance(arg, RPCAPICommand):
                        rpc_multicommand.add(arg.cmd)
                    if isinstance(arg, WebAPICommand):
                        web_multicommand.add(arg.cmd)
            except KeyError as e:
                logger.error(type(e), e, data_name)
                continue

        # create tasks for all commands that need to be sent, or no-op with sleep(0) -> None
        if (
            len(rpc_multicommand) > 0
            and self.rpc is not None
            and hasattr(self.rpc, "multicommand")
        ):
            rpc_command_task = asyncio.create_task(
                self.rpc.multicommand(*rpc_multicommand, allow_warning=allow_warning)
            )
        else:
            rpc_command_task = asyncio.create_task(asyncio.sleep(0))
        if (
            len(web_multicommand) > 0
            and self.web is not None
            and hasattr(self.web, "multicommand")
        ):
            web_command_task = asyncio.create_task(
                self.web.multicommand(*web_multicommand, allow_warning=allow_warning)
            )
        else:
            web_command_task = asyncio.create_task(asyncio.sleep(0))

        # make sure the tasks complete
        await asyncio.gather(rpc_command_task, web_command_task)

        # grab data out of the tasks
        web_command_data = web_command_task.result()
        if web_command_data is None:
            web_command_data = {}
        api_command_data = rpc_command_task.result()
        if api_command_data is None:
            api_command_data = {}

        miner_data = {}

        for data_name in include:
            try:
                fn_args = getattr(self.data_locations, str(data_name)).kwargs
                args_to_send = {k.name: None for k in fn_args}
                for arg in fn_args:
                    try:
                        if isinstance(arg, RPCAPICommand):
                            if api_command_data.get("multicommand"):
                                args_to_send[arg.name] = api_command_data[arg.cmd][0]
                            else:
                                args_to_send[arg.name] = api_command_data
                        if isinstance(arg, WebAPICommand):
                            if web_command_data is not None:
                                if web_command_data.get("multicommand"):
                                    args_to_send[arg.name] = web_command_data[arg.cmd]
                                else:
                                    if not web_command_data == {"multicommand": False}:
                                        args_to_send[arg.name] = web_command_data
                    except LookupError:
                        args_to_send[arg.name] = None
            except LookupError:
                continue
            try:
                function = getattr(
                    self, getattr(self.data_locations, str(data_name)).cmd
                )
                miner_data[data_name] = await function(**args_to_send)
            except Exception as e:
                raise APIError(
                    f"Failed to call {data_name} on {self} while getting data."
                ) from e
        return miner_data

    async def get_data(
        self,
        allow_warning: bool = False,
        include: list[str | DataOptions] | None = None,
        exclude: list[str | DataOptions] | None = None,
    ) -> MinerData:
        """Get data from the miner in the form of [`MinerData`][pyasic.data.MinerData].

        Parameters:
            allow_warning: Allow warning when an API command fails.
            include: Names of data items you want to gather. Defaults to all data.
            exclude: Names of data items to exclude.  Exclusion happens after considering included items.

        Returns:
            A [`MinerData`][pyasic.data.MinerData] instance containing data from the miner.
        """
        data = MinerData(
            ip=str(self.ip),
            device_info=self.device_info,
            expected_chips=(
                self.expected_chips * self.expected_hashboards
                if self.expected_chips is not None
                and self.expected_hashboards is not None
                else 0
            ),
            expected_hashboards=self.expected_hashboards,
            expected_fans=self.expected_fans,
            hashboards=[
                HashBoard(slot=i, expected_chips=self.expected_chips)
                for i in range(
                    self.expected_hashboards
                    if self.expected_hashboards is not None
                    else 0
                )
            ],
        )

        gathered_data = await self._get_data(
            allow_warning=allow_warning, include=include, exclude=exclude
        )
        for item in gathered_data:
            if gathered_data[item] is not None:
                setattr(data, item, gathered_data[item])

        return data


class BaseMiner(MinerProtocol):
    def __init__(self, ip: str, version: str | None = None) -> None:
        self.ip = ip

        if self.expected_chips is None and self.raw_model is not None:
            warnings.warn(
                f"Unknown chip count for miner type {self.raw_model}, "
                f"please open an issue on GitHub (https://github.com/UpstreamData/pyasic)."
            )

        # interfaces
        if self._rpc_cls is not None:
            self.rpc = self._rpc_cls(ip)
        if self._web_cls is not None:
            self.web = self._web_cls(ip)
        if self._ssh_cls is not None:
            self.ssh = self._ssh_cls(ip)


AnyMiner = TypeVar("AnyMiner", bound=BaseMiner)
