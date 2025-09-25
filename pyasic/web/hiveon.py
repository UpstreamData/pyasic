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

import json
from pathlib import Path
from typing import Any

import aiofiles
import httpx

from pyasic import APIError, settings
from pyasic.web.base import BaseWebAPI


class HiveonWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        """Initialize the old Antminer API client with a specific IP address.

        Args:
            ip (str): IP address of the Antminer device.
        """
        super().__init__(ip)
        self.username: str = "root"
        self.pwd: str = settings.get("default_hive_web_password", "root")

    async def send_command(
        self,
        command: str,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        """Send a command to the Antminer device using HTTP digest authentication.

        Args:
            command (str): The CGI command to send.
            ignore_errors (bool): If True, ignore any HTTP errors.
            allow_warning (bool): If True, proceed with warnings.
            privileged (bool): If set to True, requires elevated privileges.
            **parameters: Arbitrary keyword arguments to be sent as parameters in the request.

        Returns:
            dict: The JSON response from the device or an empty dictionary if an error occurs.
        """
        url = f"http://{self.ip}:{self.port}/cgi-bin/{command}.cgi"
        auth = httpx.DigestAuth(self.username, self.pwd)
        try:
            async with httpx.AsyncClient(transport=settings.transport()) as client:
                if parameters:
                    response = await client.post(
                        url,
                        data=parameters,
                        auth=auth,
                        timeout=settings.get("api_function_timeout", 3),
                    )
                else:
                    response = await client.get(url, auth=auth)
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error sending '{command}' to {self.ip}: {e}")
        else:
            if response.status_code == 200:
                try:
                    return response.json()
                except json.decoder.JSONDecodeError as e:
                    response_text = response.text if response.text else "empty response"
                    raise APIError(
                        f"JSON decode error for '{command}' from {self.ip}: {e} - Response: {response_text}"
                    )
        raise APIError(f"Failed to send command to miner API: {url}")

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        """Execute multiple commands simultaneously.

        Args:
            *commands (str): Multiple command strings to be executed.
            ignore_errors (bool): If True, ignore any HTTP errors.
            allow_warning (bool): If True, proceed with warnings.

        Returns:
            dict: A dictionary containing the results of all commands executed.
        """
        data = {k: None for k in commands}
        auth = httpx.DigestAuth(self.username, self.pwd)
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            for command in commands:
                try:
                    url = f"http://{self.ip}/cgi-bin/{command}.cgi"
                    ret = await client.get(url, auth=auth)
                except httpx.HTTPError:
                    pass
                else:
                    if ret.status_code == 200:
                        try:
                            json_data = ret.json()
                            data[command] = json_data
                        except json.decoder.JSONDecodeError:
                            pass
        return data

    async def get_system_info(self) -> dict:
        """Retrieve system information from the miner.

        Returns:
            dict: A dictionary containing system information of the miner.
        """
        return await self.send_command("get_system_info")

    async def get_network_info(self) -> dict:
        """Retrieve system information from the miner.

        Returns:
            dict: A dictionary containing system information of the miner.
        """
        return await self.send_command("get_network_info")

    async def blink(self, blink: bool) -> dict:
        """Control the blinking of the LED on the miner device.

        Args:
            blink (bool): True to start blinking, False to stop.

        Returns:
            dict: A dictionary response from the device after the command execution.
        """
        if blink:
            return await self.send_command("blink", action="startBlink")
        return await self.send_command("blink", action="stopBlink")

    async def reboot(self) -> dict:
        """Reboot the miner device.

        Returns:
            dict: A dictionary response from the device confirming the reboot command.
        """
        return await self.send_command("reboot")

    async def get_blink_status(self) -> dict:
        """Check the status of the LED blinking on the miner.

        Returns:
            dict: A dictionary indicating whether the LED is currently blinking.
        """
        return await self.send_command("blink", action="onPageLoaded")

    async def get_miner_conf(self) -> dict:
        """Retrieve the miner configuration from the Antminer device.

        Returns:
            dict: A dictionary containing the current configuration of the miner.
        """
        return await self.send_command("get_miner_conf")

    async def set_miner_conf(self, conf: dict) -> dict:
        """Set the configuration for the miner.

        Args:
            conf (dict): A dictionary of configuration settings to apply to the miner.

        Returns:
            dict: A dictionary response from the device after setting the configuration.
        """
        return await self.send_command("set_miner_conf", **conf)

    async def stats(self) -> dict:
        """Retrieve detailed statistical data of the mining operation.

        Returns:
            dict: Detailed statistics of the miner's operation.
        """
        return await self.send_command("miner_stats")

    async def summary(self) -> dict:
        """Get a summary of the miner's status and performance.

        Returns:
            dict: A summary of the miner's current operational status.
        """
        return await self.send_command("miner_summary")

    async def pools(self) -> dict:
        """Retrieve current pool information associated with the miner.

        Returns:
            dict: Information about the mining pools configured in the miner.
        """
        return await self.send_command("miner_pools")

    async def update_firmware(self, file: Path, keep_settings: bool = True) -> dict:
        """Perform a system update by uploading a firmware file and sending a command to initiate the update."""

        async with aiofiles.open(file, "rb") as firmware:
            file_content = await firmware.read()

        return await self.send_command(
            "upgrade",
            file=(file.name, file_content, "application/octet-stream"),
            filename=file.name,
            keep_settings=keep_settings,
        )
