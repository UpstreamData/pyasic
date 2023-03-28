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
import ipaddress
import warnings
from abc import ABC, abstractmethod
from typing import Union

from pyasic.errors import APIWarning


class BaseWebAPI(ABC):
    def __init__(self, ip: str) -> None:
        # ip address of the miner
        self.ip = ipaddress.ip_address(ip)
        self.username = "root"
        self.pwd = "root"

    def __new__(cls, *args, **kwargs):
        if cls is BaseWebAPI:
            raise TypeError(f"Only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)

    def __repr__(self):
        return f"{self.__class__.__name__}: {str(self.ip)}"

    @abstractmethod
    async def send_command(
        self,
        command: Union[str, bytes],
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **parameters: Union[str, int, bool],
    ) -> dict:
        pass

    @abstractmethod
    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        pass

    def _check_commands(self, *commands):
        allowed_commands = self.get_commands()
        return_commands = []
        for command in [*commands]:
            if command in allowed_commands:
                return_commands.append(command)
            else:
                warnings.warn(
                    f"""Removing incorrect command: {command}
If you are sure you want to use this command please use WebAPI.send_command("{command}", ignore_errors=True) instead.""",
                    APIWarning,
                )
        return return_commands

    @property
    def commands(self) -> list:
        return self.get_commands()

    def get_commands(self) -> list:
        """Get a list of command accessible to a specific type of web API on the miner.

        Returns:
            A list of all web commands that the miner supports.
        """
        return [
            func
            for func in
            # each function in self
            dir(self)
            if not func == "commands"
            if callable(getattr(self, func)) and
            # no __ or _ methods
            not func.startswith("__") and not func.startswith("_") and
            # remove all functions that are in this base class
            func
            not in [
                func for func in dir(BaseWebAPI) if callable(getattr(BaseWebAPI, func))
            ]
        ]
