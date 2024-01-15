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
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, make_dataclass
from enum import Enum
from typing import List, Optional, Tuple, TypeVar, Union

import asyncssh

from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard, MinerData
from pyasic.data.error_codes import MinerErrorData
from pyasic.errors import APIError
from pyasic.logger import logger


class DataOptions(Enum):
    MAC = "mac"
    API_VERSION = "api_ver"
    FW_VERSION = "fw_ver"
    HOSTNAME = "hostname"
    HASHRATE = "hashrate"
    EXPECTED_HASHRATE = "expected_hashrate"
    HASHBOARDS = "hashboards"
    ENVIRONMENT_TEMP = "env_temp"
    WATTAGE = "wattage"
    WATTAGE_LIMIT = "wattage_limit"
    FANS = "fans"
    FAN_PSU = "fan_psu"
    ERRORS = "errors"
    FAULT_LIGHT = "fault_light"
    IS_MINING = "is_mining"
    UPTIME = "uptime"
    CONFIG = "config"

    def __str__(self):
        return self.value


@dataclass
class RPCAPICommand:
    name: str
    cmd: str


@dataclass
class WebAPICommand:
    name: str
    cmd: str


@dataclass
class GRPCCommand(WebAPICommand):
    name: str
    cmd: str


@dataclass
class GraphQLCommand(WebAPICommand):
    name: str
    cmd: dict


@dataclass
class DataFunction:
    cmd: str
    kwargs: list[
        Union[RPCAPICommand, WebAPICommand, GRPCCommand, GraphQLCommand]
    ] = field(default_factory=list)


DataLocations = make_dataclass(
    "DataLocations",
    [(enum_value.value, str) for enum_value in DataOptions],
)
# add default value with
# [(enum_value.value, str, , DataFunction(enum_value.value)) for enum_value in DataOptions],


class BaseMiner(ABC):
    def __init__(self, ip: str, *args, **kwargs) -> None:
        # interfaces
        self.api = None
        self.web = None

        self.ssh_pwd = "root"

        # static data
        self.ip = ip
        self.api_type = None
        # type
        self.make = None
        self.raw_model = None
        self.fw_str = None
        # physical attributes
        self.expected_hashboards = 3
        self.expected_chips = 0
        self.expected_fans = 2
        # data gathering locations
        self.data_locations: DataLocations = None
        # autotuning/shutdown support
        self.supports_autotuning = False
        self.supports_shutdown = False

        # data storage
        self.api_ver = None
        self.fw_ver = None
        self.light = None
        self.config = None

    def __new__(cls, *args, **kwargs):
        if cls is BaseMiner:
            raise TypeError(f"Only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)

    def __repr__(self):
        return f"{'' if not self.api_type else self.api_type}{'' if not self.model else ' ' + self.model}: {str(self.ip)}"

    def __lt__(self, other):
        return ipaddress.ip_address(self.ip) < ipaddress.ip_address(other.ip)

    def __gt__(self, other):
        return ipaddress.ip_address(self.ip) > ipaddress.ip_address(other.ip)

    def __eq__(self, other):
        return ipaddress.ip_address(self.ip) == ipaddress.ip_address(other.ip)

    @property
    def model(self):
        model_data = [self.raw_model if self.raw_model is not None else "Unknown"]
        if self.fw_str is not None:
            model_data.append(f"({self.fw_str})")
        return " ".join(model_data)

    @property
    def pwd(self):  # noqa - Skip PyCharm inspection
        data = []
        try:
            if self.web is not None:
                data.append(f"web={self.web.pwd}")
        except TypeError:
            pass
        try:
            if self.api is not None:
                data.append(f"api={self.api.pwd}")
        except TypeError:
            pass
        return ",".join(data)

    @pwd.setter
    def pwd(self, val):
        self.ssh_pwd = val
        try:
            if self.web is not None:
                self.web.pwd = val
        except TypeError:
            pass
        try:
            if self.api is not None:
                self.api.pwd = val
        except TypeError:
            pass

    @property
    def username(self):  # noqa - Skip PyCharm inspection
        data = []
        try:
            if self.web is not None:
                data.append(f"web={self.web.username}")
        except TypeError:
            pass
        return ",".join(data)

    @username.setter
    def username(self, val):
        try:
            if self.web is not None:
                self.web.username = val
        except TypeError:
            pass

    async def _get_ssh_connection(self) -> asyncssh.connect:
        """Create a new asyncssh connection"""
        try:
            conn = await asyncssh.connect(
                str(self.ip),
                known_hosts=None,
                username="root",
                password=self.ssh_pwd,
                server_host_key_algs=["ssh-rsa"],
            )
            return conn
        except asyncssh.misc.PermissionDenied:
            try:
                conn = await asyncssh.connect(
                    str(self.ip),
                    known_hosts=None,
                    username="root",
                    password="admin",
                    server_host_key_algs=["ssh-rsa"],
                )
                return conn
            except Exception as e:
                raise ConnectionError from e
        except OSError as e:
            logging.warning(f"Connection refused: {self}")
            raise ConnectionError from e
        except Exception as e:
            raise ConnectionError from e

    async def check_light(self) -> bool:
        return await self.get_fault_light()

    @abstractmethod
    async def fault_light_on(self) -> bool:
        """Turn the fault light of the miner on and return success as a boolean.

        Returns:
            A boolean value of the success of turning the light on.
        """
        pass

    @abstractmethod
    async def fault_light_off(self) -> bool:
        """Turn the fault light of the miner off and return success as a boolean.

        Returns:
            A boolean value of the success of turning the light off.
        """
        pass

    @abstractmethod
    async def get_config(self) -> MinerConfig:
        # Not a data gathering function, since this is used for configuration
        """Get the mining configuration of the miner and return it as a [`MinerConfig`][pyasic.config.MinerConfig].

        Returns:
            A [`MinerConfig`][pyasic.config.MinerConfig] containing the pool information and mining configuration.
        """
        pass

    @abstractmethod
    async def reboot(self) -> bool:
        """Reboot the miner and return success as a boolean.

        Returns:
            A boolean value of the success of rebooting the miner.
        """
        pass

    @abstractmethod
    async def restart_backend(self) -> bool:
        """Restart the mining process of the miner (bosminer, bmminer, cgminer, etc) and return success as a boolean.

        Returns:
            A boolean value of the success of restarting the mining process.
        """
        pass

    @abstractmethod
    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        """Set the mining configuration of the miner.

        Parameters:
            config: A [`MinerConfig`][pyasic.config.MinerConfig] containing the mining config you want to switch the miner to.
            user_suffix: A suffix to append to the username when sending to the miner.
        """
        return None

    @abstractmethod
    async def stop_mining(self) -> bool:
        """Stop the mining process of the miner.

        Returns:
            A boolean value of the success of stopping the mining process.
        """
        pass

    @abstractmethod
    async def resume_mining(self) -> bool:
        """Resume the mining process of the miner.

        Returns:
            A boolean value of the success of resuming the mining process.
        """
        pass

    @abstractmethod
    async def set_power_limit(self, wattage: int) -> bool:
        """Set the power limit to be used by the miner.

        Parameters:
            wattage: The power limit to set on the miner.

        Returns:
            A boolean value of the success of setting the power limit.
        """
        pass

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(self) -> Optional[str]:
        """Get the MAC address of the miner and return it as a string.

        Returns:
            A string representing the MAC address of the miner.
        """
        return await self._get_mac()

    async def get_model(self) -> Optional[str]:
        """Get the model of the miner and return it as a string.

        Returns:
            A string representing the model of the miner.
        """
        return self.model

    async def get_api_ver(self) -> Optional[str]:
        """Get the API version of the miner and is as a string.

        Returns:
            API version as a string.
        """
        return await self._get_api_ver()

    async def get_fw_ver(self) -> Optional[str]:
        """Get the firmware version of the miner and is as a string.

        Returns:
            Firmware version as a string.
        """
        return await self._get_fw_ver()

    async def get_version(self) -> Tuple[Optional[str], Optional[str]]:
        """Get the API version and firmware version of the miner and return them as strings.

        Returns:
            A tuple of (API version, firmware version) as strings.
        """
        api_ver = await self.get_api_ver()
        fw_ver = await self.get_fw_ver()
        return api_ver, fw_ver

    async def get_hostname(self) -> Optional[str]:
        """Get the hostname of the miner and return it as a string.

        Returns:
            A string representing the hostname of the miner.
        """
        return await self._get_hostname()

    async def get_hashrate(self) -> Optional[float]:
        """Get the hashrate of the miner and return it as a float in TH/s.

        Returns:
            Hashrate of the miner in TH/s as a float.
        """
        return await self._get_hashrate()

    async def get_hashboards(self) -> List[HashBoard]:
        """Get hashboard data from the miner in the form of [`HashBoard`][pyasic.data.HashBoard].

        Returns:
            A [`HashBoard`][pyasic.data.HashBoard] instance containing hashboard data from the miner.
        """
        return await self._get_hashboards()

    async def get_env_temp(self) -> Optional[float]:
        """Get environment temp from the miner as a float.

        Returns:
            Environment temp of the miner as a float.
        """
        return await self._get_env_temp()

    async def get_wattage(self) -> Optional[int]:
        """Get wattage from the miner as an int.

        Returns:
            Wattage of the miner as an int.
        """
        return await self._get_wattage()

    async def get_wattage_limit(self) -> Optional[int]:
        """Get wattage limit from the miner as an int.

        Returns:
            Wattage limit of the miner as an int.
        """
        return await self._get_wattage_limit()

    async def get_fans(self) -> List[Fan]:
        """Get fan data from the miner in the form [fan_1, fan_2, fan_3, fan_4].

        Returns:
            A list of fan data.
        """
        return await self._get_fans()

    async def get_fan_psu(self) -> Optional[int]:
        """Get PSU fan speed from the miner.

        Returns:
            PSU fan speed.
        """
        return await self._get_fan_psu()

    async def get_errors(self) -> List[MinerErrorData]:
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
        return await self._get_fault_light()

    async def get_expected_hashrate(self) -> Optional[float]:
        """Get the nominal hashrate from factory if available.

        Returns:
            A float value of nominal hashrate in TH/s.
        """
        return await self._get_expected_hashrate()

    async def is_mining(self) -> Optional[bool]:
        """Check whether the miner is mining.

        Returns:
            A boolean value representing if the miner is mining.
        """
        return await self._is_mining()

    async def get_uptime(self) -> Optional[int]:
        """Get the uptime of the miner in seconds.

        Returns:
            The uptime of the miner in seconds.
        """
        return await self._get_uptime()

    @abstractmethod
    async def _get_mac(self, *args, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    async def _get_api_ver(self, *args, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    async def _get_fw_ver(self, *args, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    async def _get_hostname(self, *args, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    async def _get_hashrate(self, *args, **kwargs) -> Optional[float]:
        pass

    @abstractmethod
    async def _get_hashboards(self, *args, **kwargs) -> List[HashBoard]:
        pass

    @abstractmethod
    async def _get_env_temp(self, *args, **kwargs) -> Optional[float]:
        pass

    @abstractmethod
    async def _get_wattage(self, *args, **kwargs) -> Optional[int]:
        pass

    @abstractmethod
    async def _get_wattage_limit(self, *args, **kwargs) -> Optional[int]:
        pass

    @abstractmethod
    async def _get_fans(self, *args, **kwargs) -> List[Fan]:
        pass

    @abstractmethod
    async def _get_fan_psu(self, *args, **kwargs) -> Optional[int]:
        pass

    @abstractmethod
    async def _get_errors(self, *args, **kwargs) -> List[MinerErrorData]:
        pass

    @abstractmethod
    async def _get_fault_light(self, *args, **kwargs) -> bool:
        pass

    @abstractmethod
    async def _get_expected_hashrate(self, *args, **kwargs) -> Optional[float]:
        pass

    @abstractmethod
    async def _is_mining(self, *args, **kwargs) -> Optional[bool]:
        pass

    @abstractmethod
    async def _get_uptime(self, *args, **kwargs) -> Optional[int]:
        pass

    async def _get_data(
        self,
        allow_warning: bool,
        include: List[Union[str, DataOptions]] = None,
        exclude: List[Union[str, DataOptions]] = None,
    ) -> dict:
        if include is not None:
            include = [str(i) for i in include]
        else:
            # everything
            include = [str(enum_value.value) for enum_value in DataOptions]

        if exclude is not None:
            for item in exclude:
                if str(item) in include:
                    include.remove(str(item))

        api_multicommand = set()
        web_multicommand = []
        for data_name in include:
            try:
                fn_args = getattr(self.data_locations, data_name).kwargs
                for arg in fn_args:
                    if isinstance(arg, RPCAPICommand):
                        api_multicommand.add(arg.cmd)
                    if isinstance(arg, WebAPICommand):
                        if arg.cmd not in web_multicommand:
                            web_multicommand.append(arg.cmd)
            except KeyError as e:
                logger.error(e, data_name)
                continue

        if len(api_multicommand) > 0:
            api_command_task = asyncio.create_task(
                self.api.multicommand(*api_multicommand, allow_warning=allow_warning)
            )
        else:
            api_command_task = asyncio.sleep(0)
        if len(web_multicommand) > 0:
            web_command_task = asyncio.create_task(
                self.web.multicommand(*web_multicommand, allow_warning=allow_warning)
            )
        else:
            web_command_task = asyncio.sleep(0)

        web_command_data = await web_command_task
        if web_command_data is None:
            web_command_data = {}

        api_command_data = await api_command_task
        if api_command_data is None:
            api_command_data = {}

        miner_data = {}

        for data_name in include:
            try:
                fn_args = getattr(self.data_locations, data_name).kwargs
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
                function = getattr(self, getattr(self.data_locations, data_name).cmd)
                miner_data[data_name] = await function(**args_to_send)
            except Exception as e:
                raise APIError(
                    f"Failed to call {data_name} on {self} while getting data."
                ) from e
        return miner_data

    async def get_data(
        self,
        allow_warning: bool = False,
        include: List[Union[str, DataOptions]] = None,
        exclude: List[Union[str, DataOptions]] = None,
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
            make=self.make,
            model=self.model,
            expected_chips=self.expected_chips * self.expected_hashboards,
            expected_hashboards=self.expected_hashboards,
            hashboards=[
                HashBoard(slot=i, expected_chips=self.expected_chips)
                for i in range(self.expected_hashboards)
            ],
        )

        gathered_data = await self._get_data(
            allow_warning=allow_warning, include=include, exclude=exclude
        )
        for item in gathered_data:
            if gathered_data[item] is not None:
                setattr(data, item, gathered_data[item])

        return data


AnyMiner = TypeVar("AnyMiner", bound=BaseMiner)
