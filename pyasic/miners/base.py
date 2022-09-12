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
from typing import TypeVar

from pyasic.data import MinerData
from pyasic.config import MinerConfig


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
        pass

    @abstractmethod
    async def fault_light_off(self) -> bool:
        pass

    @abstractmethod
    async def check_light(self) -> bool:
        pass

    @abstractmethod
    async def get_config(self) -> MinerConfig:
        pass

    @abstractmethod
    async def get_hostname(self) -> str:
        pass

    @abstractmethod
    async def get_model(self) -> str:
        pass

    @abstractmethod
    async def reboot(self) -> bool:
        pass

    @abstractmethod
    async def restart_backend(self) -> bool:
        pass

    @abstractmethod
    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        return None

    @abstractmethod
    async def get_mac(self) -> str:
        pass

    @abstractmethod
    async def get_errors(self) -> list:
        pass

    @abstractmethod
    async def get_data(self) -> MinerData:
        return MinerData(ip=str(self.ip))


AnyMiner = TypeVar("AnyMiner", bound=BaseMiner)
