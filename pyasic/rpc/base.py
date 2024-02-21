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
import json
import logging
import re
import warnings
from typing import Union

from pyasic.errors import APIError, APIWarning
from pyasic.misc import validate_command_output


class BaseMinerRPCAPI:
    def __init__(self, ip: str, port: int = 4028, api_ver: str = "0.0.0") -> None:
        # api port, should be 4028
        self.port = port
        # ip address of the miner
        self.ip = ipaddress.ip_address(ip)
        # api version if known
        self.api_ver = api_ver

        self.pwd = None

    def __new__(cls, *args, **kwargs):
        if cls is BaseMinerRPCAPI:
            raise TypeError(f"Only children of '{cls.__name__}' may be instantiated")
        return object.__new__(cls)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {str(self.ip)}"

    async def send_command(
        self,
        command: Union[str, bytes],
        parameters: Union[str, int, bool] = None,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **kwargs,
    ) -> dict:
        """Send an API command to the miner and return the result.

        Parameters:
            command: The command to sent to the miner.
            parameters: Any additional parameters to be sent with the command.
            ignore_errors: Whether to raise APIError when the command returns an error.
            allow_warning: Whether to warn if the command fails.

        Returns:
            The return data from the API command parsed from JSON into a dict.
        """
        logging.debug(
            f"{self} - (Send Privileged Command) - {command} "
            + f"with args {parameters}"
            if parameters
            else ""
        )
        # create the command
        cmd = {"command": command, **kwargs}
        if parameters:
            cmd["parameter"] = parameters

        # send the command
        data = await self._send_bytes(json.dumps(cmd).encode("utf-8"))

        if data is None:
            raise APIError("No data returned from the API.")

        if data == b"Socket connect failed: Connection refused\n":
            if not ignore_errors:
                raise APIError(data.decode("utf-8"))
            return {}

        data = self._load_api_data(data)

        # check for if the user wants to allow errors to return
        validation = validate_command_output(data)
        if not validation[0]:
            if not ignore_errors:
                # validate the command succeeded
                raise APIError(f"{command}: {validation[1]}")
            if allow_warning:
                logging.warning(
                    f"{self.ip}: API Command Error: {command}: {validation[1]}"
                )

        logging.debug(f"{self} - (Send Command) - Received data.")
        return data

    # Privileged command handler, only used by whatsminers, defined here for consistency.
    async def send_privileged_command(self, *args, **kwargs) -> dict:
        return await self.send_command(*args, **kwargs)

    async def multicommand(self, *commands: str, allow_warning: bool = True) -> dict:
        """Creates and sends multiple commands as one command to the miner.

        Parameters:
            *commands: The commands to send as a multicommand to the miner.
            allow_warning: A boolean to supress APIWarnings.

        """
        # make sure we can actually run each command, otherwise they will fail
        commands = self._check_commands(*commands)
        # standard multicommand format is "command1+command2"
        # doesn't work for S19 which uses the backup _send_split_multicommand
        command = "+".join(commands)
        try:
            data = await self.send_command(command, allow_warning=allow_warning)
        except APIError:
            data = await self._send_split_multicommand(*commands)
        data["multicommand"] = True
        return data

    async def _send_split_multicommand(
        self, *commands, allow_warning: bool = True
    ) -> dict:
        tasks = {}
        # send all commands individually
        for cmd in commands:
            tasks[cmd] = asyncio.create_task(
                self.send_command(cmd, allow_warning=allow_warning)
            )

        await asyncio.gather(*[tasks[cmd] for cmd in tasks], return_exceptions=True)

        data = {}
        for cmd in tasks:
            try:
                result = tasks[cmd].result()
                if result is None or result == {}:
                    result = {}
                data[cmd] = [result]
            except APIError:
                pass

        return data

    @property
    def commands(self) -> list:
        return self.get_commands()

    def get_commands(self) -> list:
        """Get a list of command accessible to a specific type of API on the miner.

        Returns:
            A list of all API commands that the miner supports.
        """
        return [
            func
            for func in
            # each function in self
            dir(self)
            if not func in ["commands", "open_api"]
            if callable(getattr(self, func)) and
            # no __ or _ methods
            not func.startswith("__") and not func.startswith("_") and
            # remove all functions that are in this base class
            func
            not in [
                func
                for func in dir(BaseMinerRPCAPI)
                if callable(getattr(BaseMinerRPCAPI, func))
            ]
        ]

    def _check_commands(self, *commands) -> list:
        allowed_commands = self.commands
        return_commands = []

        for command in commands:
            if command in allowed_commands:
                return_commands.append(command)
            else:
                warnings.warn(
                    f"""Removing incorrect command: {command}
If you are sure you want to use this command please use API.send_command("{command}", ignore_errors=True) instead.""",
                    APIWarning,
                )
        return return_commands

    async def _send_bytes(
        self,
        data: bytes,
        *,
        port: int = None,
        timeout: int = 100,
    ) -> bytes:
        if port is None:
            port = self.port
        logging.debug(f"{self} - ([Hidden] Send Bytes) - Sending")
        try:
            # get reader and writer streams
            reader, writer = await asyncio.open_connection(str(self.ip), port)
        # handle OSError 121
        except OSError as e:
            if e.errno == 121:
                logging.warning(
                    f"{self} - ([Hidden] Send Bytes) - Semaphore timeout expired."
                )
            return b"{}"

        # send the command
        data_task = asyncio.create_task(self._read_bytes(reader, timeout=timeout))
        logging.debug(f"{self} - ([Hidden] Send Bytes) - Writing")
        writer.write(data)
        logging.debug(f"{self} - ([Hidden] Send Bytes) - Draining")
        await writer.drain()

        await data_task
        ret_data = data_task.result()

        # close the connection
        logging.debug(f"{self} - ([Hidden] Send Bytes) - Closing")
        writer.close()
        await writer.wait_closed()

        return ret_data

    async def _read_bytes(self, reader: asyncio.StreamReader, timeout: int) -> bytes:
        ret_data = b""

        # loop to receive all the data
        logging.debug(f"{self} - ([Hidden] Send Bytes) - Receiving")
        try:
            ret_data = await asyncio.wait_for(reader.read(), timeout=timeout)
        except (asyncio.CancelledError, asyncio.TimeoutError) as e:
            raise e
        except Exception as e:
            logging.warning(f"{self} - ([Hidden] Send Bytes) - API Command Error {e}")
        return ret_data

    @staticmethod
    def _load_api_data(data: bytes) -> dict:
        # some json from the API returns with a null byte (\x00) on the end
        if data.endswith(b"\x00"):
            # handle the null byte
            str_data = data.decode("utf-8")[:-1]
        else:
            # no null byte
            str_data = data.decode("utf-8")
        # fix an error with a btminer return having an extra comma that breaks json.loads()
        str_data = str_data.replace(",}", "}")
        # fix an error with a btminer return having a newline that breaks json.loads()
        str_data = str_data.replace("\n", "")
        # fix an error with a bmminer return not having a specific comma that breaks json.loads()
        str_data = str_data.replace("}{", "},{")
        # fix an error with a bmminer return having a specific comma that breaks json.loads()
        str_data = str_data.replace("[,{", "[{")
        # fix an error with a btminer return having a missing comma. (2023-01-06 version)
        str_data = str_data.replace('""temp0', '","temp0')
        # fix an error with Avalonminers returning inf and nan
        str_data = str_data.replace("info", "1nfo")
        str_data = str_data.replace("inf", "0")
        str_data = str_data.replace("1nfo", "info")
        str_data = str_data.replace("nan", "0")
        # fix whatever this garbage from avalonminers is `,"id":1}`
        if str_data.startswith(","):
            str_data = f"{{{str_data[1:]}"
        # try to fix an error with overflowing the receive buffer
        # this can happen in cases such as bugged btminers returning arbitrary length error info with 100s of errors.
        if not str_data.endswith("}"):
            str_data = ",".join(str_data.split(",")[:-1]) + "}"

        # fix a really nasty bug with whatsminer API v2.0.4 where they return a list structured like a dict
        if re.search(r"\"error_code\":\[\".+\"\]", str_data):
            str_data = str_data.replace("[", "{").replace("]", "}")

        # parse the json
        try:
            parsed_data = json.loads(str_data)
        except json.decoder.JSONDecodeError as e:
            raise APIError(f"Decode Error {e}: {str_data}")
        return parsed_data
