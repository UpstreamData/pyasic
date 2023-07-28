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
from typing import List, Optional, Tuple, TypeVar

import asyncssh

from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard, MinerData
from pyasic.data.error_codes import MinerErrorData
from pyasic.logger import logger


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
        self.model = None
        # physical attributes
        self.ideal_hashboards = 3
        self.nominal_chips = 0
        self.fan_count = 2
        # data gathering locations
        self.data_locations = None
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
        # Not a data gathering function, since this is used for configuration and not MinerData
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

    @abstractmethod
    async def get_mac(self, *args, **kwargs) -> Optional[str]:
        """Get the MAC address of the miner and return it as a string.

        Returns:
            A string representing the MAC address of the miner.
        """
        pass

    async def get_model(self) -> Optional[str]:
        """Get the model of the miner and return it as a string.

        Returns:
            A string representing the model of the miner.
        """
        return self.model

    @abstractmethod
    async def get_api_ver(self, *args, **kwargs) -> Optional[str]:
        """Get the API version of the miner and is as a string.

        Returns:
            API version as a string.
        """
        pass

    @abstractmethod
    async def get_fw_ver(self, *args, **kwargs) -> Optional[str]:
        """Get the firmware version of the miner and is as a string.

        Returns:
            Firmware version as a string.
        """
        pass

    @abstractmethod
    async def get_version(self, *args, **kwargs) -> Tuple[Optional[str], Optional[str]]:
        """Get the API version and firmware version of the miner and return them as strings.

        Returns:
            A tuple of (API version, firmware version) as strings.
        """
        pass

    @abstractmethod
    async def get_hostname(self, *args, **kwargs) -> Optional[str]:
        """Get the hostname of the miner and return it as a string.

        Returns:
            A string representing the hostname of the miner.
        """
        pass

    @abstractmethod
    async def get_hashrate(self, *args, **kwargs) -> Optional[float]:
        """Get the hashrate of the miner and return it as a float in TH/s.

        Returns:
            Hashrate of the miner in TH/s as a float.
        """
        pass

    @abstractmethod
    async def get_hashboards(self, *args, **kwargs) -> List[HashBoard]:
        """Get hashboard data from the miner in the form of [`HashBoard`][pyasic.data.HashBoard].

        Returns:
            A [`HashBoard`][pyasic.data.HashBoard] instance containing hashboard data from the miner.
        """
        pass

    @abstractmethod
    async def get_env_temp(self, *args, **kwargs) -> Optional[float]:
        """Get environment temp from the miner as a float.

        Returns:
            Environment temp of the miner as a float.
        """
        pass

    @abstractmethod
    async def get_wattage(self, *args, **kwargs) -> Optional[int]:
        """Get wattage from the miner as an int.

        Returns:
            Wattage of the miner as an int.
        """
        pass

    @abstractmethod
    async def get_wattage_limit(self, *args, **kwargs) -> Optional[int]:
        """Get wattage limit from the miner as an int.

        Returns:
            Wattage limit of the miner as an int.
        """
        pass

    @abstractmethod
    async def get_fans(self, *args, **kwargs) -> List[Fan]:
        """Get fan data from the miner in the form [fan_1, fan_2, fan_3, fan_4].

        Returns:
            A list of fan data.
        """
        pass

    @abstractmethod
    async def get_fan_psu(self, *args, **kwargs) -> Optional[int]:
        """Get PSU fan speed from the miner.

        Returns:
            PSU fan speed.
        """
        pass

    @abstractmethod
    async def get_pools(self, *args, **kwargs) -> List[dict]:
        """Get pool information from the miner.

        Returns:
            Pool groups and quotas in a list of dicts.
        """
        pass

    @abstractmethod
    async def get_errors(self, *args, **kwargs) -> List[MinerErrorData]:
        """Get a list of the errors the miner is experiencing.

        Returns:
            A list of error classes representing different errors.
        """
        pass

    @abstractmethod
    async def get_fault_light(self, *args, **kwargs) -> bool:
        """Check the status of the fault light and return on or off as a boolean.

        Returns:
            A boolean value where `True` represents on and `False` represents off.
        """
        pass

    @abstractmethod
    async def get_nominal_hashrate(self, *args, **kwargs) -> Optional[float]:
        """Get the nominal hashrate from factory if available.

        Returns:
            A float value of nominal hashrate in TH/s.
        """
        pass

    @abstractmethod
    async def is_mining(self, *args, **kwargs) -> Optional[bool]:
        """Check whether the miner is mining.

        Returns:
            A boolean value representing if the miner is mining.
        """
        pass

    @abstractmethod
    async def get_uptime(self, *args, **kwargs) -> Optional[int]:
        """Get the uptime of the miner in seconds.

        Returns:
            The uptime of the miner in seconds.
        """
        pass

    async def _get_data(self, allow_warning: bool, data_to_get: list = None) -> dict:
        if not data_to_get:
            # everything
            data_to_get = list(self.data_locations.keys())

        api_multicommand = set()
        web_multicommand = set()
        for data_name in data_to_get:
            try:
                fn_args = self.data_locations[data_name]["kwargs"]
                for arg_name in fn_args:
                    if fn_args[arg_name].get("api"):
                        api_multicommand.add(fn_args[arg_name]["api"])
                    if fn_args[arg_name].get("web"):
                        web_multicommand.add(fn_args[arg_name]["web"])
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

        from datetime import datetime

        web_command_data = await web_command_task
        if web_command_data is None:
            web_command_data = {}

        api_command_data = await api_command_task
        if api_command_data is None:
            api_command_data = {}

        miner_data = {}

        for data_name in data_to_get:
            try:
                fn_args = self.data_locations[data_name]["kwargs"]
                args_to_send = {k: None for k in fn_args}
                for arg_name in fn_args:
                    try:
                        if fn_args[arg_name].get("api"):
                            if api_command_data.get("multicommand"):
                                args_to_send[arg_name] = api_command_data[
                                    fn_args[arg_name]["api"]
                                ][0]
                            else:
                                args_to_send[arg_name] = api_command_data
                        if fn_args[arg_name].get("web"):
                            if web_command_data is not None:
                                if web_command_data.get("multicommand"):
                                    args_to_send[arg_name] = web_command_data[
                                        fn_args[arg_name]["web"]
                                    ]
                                else:
                                    if not web_command_data == {"multicommand": False}:
                                        args_to_send[arg_name] = web_command_data
                    except LookupError:
                        args_to_send[arg_name] = None
            except LookupError:
                continue

            function = getattr(self, self.data_locations[data_name]["cmd"])
            if not data_name == "pools":
                miner_data[data_name] = await function(**args_to_send)
            else:
                pools_data = await function(**args_to_send)
                if pools_data:
                    try:
                        miner_data["pool_1_url"] = pools_data[0]["pool_1_url"]
                        miner_data["pool_1_user"] = pools_data[0]["pool_1_user"]
                    except KeyError:
                        pass
                    if len(pools_data) > 1:
                        miner_data["pool_2_url"] = pools_data[1]["pool_1_url"]
                        miner_data["pool_2_user"] = pools_data[1]["pool_1_user"]
                        miner_data[
                            "pool_split"
                        ] = f"{pools_data[0]['quota']}/{pools_data[1]['quota']}"
                    else:
                        try:
                            miner_data["pool_2_url"] = pools_data[0]["pool_2_url"]
                            miner_data["pool_2_user"] = pools_data[0]["pool_2_user"]
                            miner_data["quota"] = "0"
                        except KeyError:
                            pass
        return miner_data

    async def get_data(
        self, allow_warning: bool = False, data_to_get: list = None
    ) -> MinerData:
        """Get data from the miner in the form of [`MinerData`][pyasic.data.MinerData].

        Parameters:
            allow_warning: Allow warning when an API command fails.
            data_to_get: Names of data items you want to gather. Defaults to all data.

        Returns:
            A [`MinerData`][pyasic.data.MinerData] instance containing data from the miner.
        """
        data = MinerData(
            ip=str(self.ip),
            make=self.make,
            ideal_chips=self.nominal_chips * self.ideal_hashboards,
            ideal_hashboards=self.ideal_hashboards,
            hashboards=[
                HashBoard(slot=i, expected_chips=self.nominal_chips)
                for i in range(self.ideal_hashboards)
            ],
        )

        gathered_data = await self._get_data(allow_warning, data_to_get=data_to_get)
        for item in gathered_data:
            if gathered_data[item] is not None:
                setattr(data, item, gathered_data[item])

        return data


AnyMiner = TypeVar("AnyMiner", bound=BaseMiner)
