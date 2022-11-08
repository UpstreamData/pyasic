#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import asyncssh
import logging
import ipaddress
from abc import ABC, abstractmethod
from typing import TypeVar, List, Union

from pyasic.data import MinerData
from pyasic.config import MinerConfig
from pyasic.data.error_codes import (
    WhatsminerError,
    BraiinsOSError,
    InnosiliconError,
    X19Error,
    MinerErrorData,
)


class BaseMiner(ABC):
    def __init__(self, *args) -> None:
        self.ip = None
        self.uname = "root"
        self.pwd = "admin"
        self.api = None
        self.api_type = None
        self.model = None
        self.light = None
        self.hostname = None
        self.nominal_chips = 1
        self.version = None
        self.fan_count = 2
        self.config = None
        self.ideal_hashboards = 3

    def __new__(cls, *args, **kwargs):
        if cls is BaseMiner:
            raise TypeError(f"Only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)

    def __repr__(self):
        return f"{'' if not self.api_type else self.api_type} {'' if not self.model else self.model}: {str(self.ip)}"

    def __lt__(self, other):
        return ipaddress.ip_address(self.ip) < ipaddress.ip_address(other.ip)

    def __gt__(self, other):
        return ipaddress.ip_address(self.ip) > ipaddress.ip_address(other.ip)

    def __eq__(self, other):
        return ipaddress.ip_address(self.ip) == ipaddress.ip_address(other.ip)

    async def _get_ssh_connection(self) -> asyncssh.connect:
        """Create a new asyncssh connection"""
        try:
            conn = await asyncssh.connect(
                str(self.ip),
                known_hosts=None,
                username=self.uname,
                password=self.pwd,
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
                raise e
        except OSError as e:
            logging.warning(f"Connection refused: {self}")
            raise e
        except Exception as e:
            raise e

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
    async def check_light(self) -> bool:
        """Check the status and return on or off as a boolean.

        Returns:
            A boolean value where `True` represents on and `False` represents off.
        """
        pass

    @abstractmethod
    async def get_config(self) -> MinerConfig:
        """Get the mining configuration of the miner and return it as a [`MinerConfig`][pyasic.config.MinerConfig].

        Returns:
            A [`MinerConfig`][pyasic.config.MinerConfig] containing the pool information and mining configuration.
        """
        pass

    @abstractmethod
    async def get_hostname(self) -> str:
        """Get the hostname of the miner and return it as a string.

        Returns:
            A string representing the hostname of the miner.
        """
        pass

    @abstractmethod
    async def get_model(self) -> str:
        """Get the model of the miner and return it as a string.

        Returns:
            A string representing the model of the miner.
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
    async def get_mac(self) -> str:
        """Get the MAC address of the miner and return it as a string.

        Returns:
            A string representing the MAC address of the miner.
        """
        pass

    @abstractmethod
    async def get_errors(self) -> List[MinerErrorData]:
        """Get a list of the errors the miner is experiencing.

        Returns:
            A list of error classes representing different errors.
        """
        pass

    @abstractmethod
    async def get_data(self, allow_warning: bool = True) -> MinerData:
        """Get data from the miner in the form of [`MinerData`][pyasic.data.MinerData].

        Returns:
            A [`MinerData`][pyasic.data.MinerData] instance containing data from the miner.
        """
        return MinerData(ip=str(self.ip))

    @abstractmethod
    async def stop_mining(self) -> bool:
        """Stop the mining process of the miner.

        Returns:
            A boolean value of the success of stopping the mining process.
        """
        pass

    @abstractmethod
    async def resume_mining(self) -> bool:
        """Stop the mining process of the miner.

        Returns:
            A boolean value of the success of resuming the mining process.
        """
        pass


AnyMiner = TypeVar("AnyMiner", bound=BaseMiner)
