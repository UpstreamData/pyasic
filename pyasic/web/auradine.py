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
import json
import warnings
from typing import Any

import httpx

from pyasic import settings
from pyasic.errors import APIError
from pyasic.misc import validate_command_output
from pyasic.web.base import BaseWebAPI


class AuradineWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        """Initializes the API client for interacting with Auradine mining devices.

        Args:
            ip (str): IP address of the Auradine miner.
        """
        super().__init__(ip)
        self.username = "admin"
        self.pwd = settings.get("default_auradine_web_password", "admin")
        self.port = 8080
        self.token = None

    async def auth(self) -> str | None:
        """Authenticate and retrieve a web token from the Auradine miner.

        Returns:
            str | None: A token if authentication is successful, None otherwise.
        """
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            try:
                auth = await client.post(
                    f"http://{self.ip}:{self.port}/token",
                    json={
                        "command": "token",
                        "user": self.username,
                        "password": self.pwd,
                    },
                )
            except httpx.HTTPError:
                warnings.warn(f"Could not authenticate web token with miner: {self}")
            else:
                json_auth = auth.json()
                try:
                    self.token = json_auth["Token"][0]["Token"]
                except LookupError:
                    return None
            return self.token

    async def send_command(
        self,
        command: str | bytes,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        """Send a command to the Auradine miner, handling authentication and retries.

        Args:
            command (str | bytes): The specific command to execute.
            ignore_errors (bool): Whether to ignore HTTP errors.
            allow_warning (bool): Whether to proceed with warnings.
            privileged (bool): Whether the command requires privileged access.
            **parameters: Additional parameters for the command.

        Returns:
            dict: The JSON response from the device.
        """
        post = privileged or not parameters == {}
        if not parameters == {}:
            parameters["command"] = command

        if self.token is None:
            await self.auth()
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            for i in range(settings.get("get_data_retries", 1)):
                try:
                    if post:
                        response = await client.post(
                            f"http://{self.ip}:{self.port}/{command}",
                            headers={"Token": self.token},
                            timeout=settings.get("api_function_timeout", 5),
                            json=parameters,
                        )
                    else:
                        response = await client.get(
                            f"http://{self.ip}:{self.port}/{command}",
                            headers={"Token": self.token},
                            timeout=settings.get("api_function_timeout", 5),
                        )
                    json_data = response.json()
                    validation = validate_command_output(json_data)
                    if not validation[0]:
                        if i == settings.get("get_data_retries", 1):
                            raise APIError(validation[1])
                        # refresh the token, retry
                        await self.auth()
                        continue
                    return json_data
                except (httpx.HTTPError, json.JSONDecodeError):
                    pass

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        """Execute multiple commands simultaneously on the Auradine miner.

        Args:
            *commands (str): Commands to execute.
            ignore_errors (bool): Whether to ignore errors during command execution.
            allow_warning (bool): Whether to proceed despite warnings.

        Returns:
            dict: A dictionary containing responses for all commands executed.
        """
        tasks = {}
        # send all commands individually
        for cmd in commands:
            tasks[cmd] = asyncio.create_task(
                self.send_command(cmd, allow_warning=allow_warning)
            )

        await asyncio.gather(*[tasks[cmd] for cmd in tasks], return_exceptions=True)

        data = {"multicommand": True}
        for cmd in tasks:
            try:
                result = tasks[cmd].result()
                if result is None or result == {}:
                    result = {}
                data[cmd] = result
            except APIError:
                pass

        return data

    async def factory_reset(self) -> dict:
        """Perform a factory reset on the Auradine miner.

        Returns:
            dict: A dictionary indicating the result of the reset operation.
        """
        return await self.send_command("factory-reset", privileged=True)

    async def get_fan(self) -> dict:
        """Retrieve the current fan status from the Auradine miner.

        Returns:
            dict: A dictionary containing the current fan status.
        """
        return await self.send_command("fan")

    async def set_fan(self, fan: int, speed_pct: int) -> dict:
        """Set the speed of a specific fan on the Auradine miner.

        Args:
            fan (int): The index of the fan to control.
            speed_pct (int): The speed percentage to set for the fan.

        Returns:
            dict: A dictionary indicating the result of the operation.
        """
        return await self.send_command("fan", index=fan, percentage=speed_pct)

    async def firmware_upgrade(self, url: str = None, version: str = "latest") -> dict:
        """Upgrade the firmware of the Auradine miner.

        Args:
            url (str, optional): The URL to download the firmware from.
            version (str, optional): The version of the firmware to upgrade to, defaults to 'latest'.

        Returns:
            dict: A dictionary indicating the result of the firmware upgrade.
        """
        if url is not None:
            return await self.send_command("firmware-upgrade", url=url)
        return await self.send_command("firmware-upgrade", version=version)

    async def get_frequency(self) -> dict:
        """Retrieve the current frequency settings of the Auradine miner.

        Returns:
            dict: A dictionary containing the frequency settings.
        """
        return await self.send_command("frequency")

    async def set_frequency(self, board: int, frequency: float) -> dict:
        """Set the frequency for a specific board on the Auradine miner.

        Args:
            board (int): The index of the board to configure.
            frequency (float): The frequency in MHz to set for the board.

        Returns:
            dict: A dictionary indicating the result of setting the frequency.
        """
        return await self.send_command("frequency", board=board, frequency=frequency)

    async def ipreport(self) -> dict:
        """Generate an IP report for the Auradine miner.

        Returns:
            dict: A dictionary containing the IP report details.
        """
        return await self.send_command("ipreport")

    async def get_led(self) -> dict:
        """Retrieve the current LED status from the Auradine miner.

        Returns:
            dict: A dictionary containing the current status of the LED settings.
        """
        return await self.send_command("led")

    async def set_led(self, code: int) -> dict:
        """Set the LED code on the Auradine miner.

        Args:
            code (int): The code that determines the LED behavior.

        Returns:
            dict: A dictionary indicating the result of the operation.
        """
        return await self.send_command("led", code=code)

    async def set_led_custom(self, code: int, led_1: int, led_2: int, msg: str) -> dict:
        """Set custom LED configurations including messages.

        Args:
            code (int): The LED code to set.
            led_1 (int): The first LED indicator number.
            led_2 (int): The second LED indicator number.
            msg (str): The message to display or represent with LEDs.

        Returns:
            dict: A dictionary indicating the result of the custom LED configuration.
        """
        return await self.send_command(
            "led", code=code, led1=led_1, led2=led_2, msg=msg
        )

    async def get_mode(self) -> dict:
        """Retrieve the current operational mode of the Auradine miner.

        Returns:
            dict: A dictionary containing the current mode settings.
        """
        return await self.send_command("mode")

    async def set_mode(self, **kwargs) -> dict:
        """Set the operational mode of the Auradine miner.

        Args:
            **kwargs: Mode settings specified as keyword arguments.

        Returns:
            dict: A dictionary indicating the result of the mode setting operation.
        """
        return await self.send_command("mode", **kwargs)

    async def get_network(self) -> dict:
        """Retrieve the network configuration settings of the Auradine miner.

        Returns:
            dict: A dictionary containing the network configuration details.
        """
        return await self.send_command("network")

    async def set_network(self, **kwargs) -> dict:
        """Set the network configuration of the Auradine miner.

        Args:
            **kwargs: Network settings specified as keyword arguments.

        Returns:
            dict: A dictionary indicating the result of the network configuration.
        """
        return await self.send_command("network", **kwargs)

    async def password(self, password: str) -> dict:
        """Change the password used for accessing the Auradine miner.

        Args:
            password (str): The new password to set.

        Returns:
            dict: A dictionary indicating the result of the password change operation.
        """
        res = await self.send_command(
            "password", user=self.username, old=self.pwd, new=password
        )
        self.pwd = password
        return res

    async def get_psu(self) -> dict:
        """Retrieve the status of the power supply unit (PSU) from the Auradine miner.

        Returns:
            dict: A dictionary containing the PSU status.
        """
        return await self.send_command("psu")

    async def set_psu(self, voltage: float) -> dict:
        """Set the voltage for the power supply unit of the Auradine miner.

        Args:
            voltage (float): The voltage level to set for the PSU.

        Returns:
            dict: A dictionary indicating the result of setting the PSU voltage.
        """
        return await self.send_command("psu", voltage=voltage)

    async def get_register(self) -> dict:
        """Retrieve registration information from the Auradine miner.

        Returns:
            dict: A dictionary containing the registration details.
        """
        return await self.send_command("register")

    async def set_register(self, company: str) -> dict:
        """Set the registration information for the Auradine miner.

        Args:
            company (str): The company name to register the miner under.

        Returns:
            dict: A dictionary indicating the result of the registration operation.
        """
        return await self.send_command("register", parameter=company)

    async def reboot(self) -> dict:
        """Reboot the Auradine miner.

        Returns:
            dict: A dictionary indicating the result of the reboot operation.
        """
        return await self.send_command("restart", privileged=True)

    async def restart_gcminer(self) -> dict:
        """Restart the GCMiner application on the Auradine miner.

        Returns:
            dict: A dictionary indicating the result of the GCMiner restart operation.
        """
        return await self.send_command("restart", parameter="gcminer")

    async def restart_api_server(self) -> dict:
        """Restart the API server on the Auradine miner.

        Returns:
            dict: A dictionary indicating the result of the API server restart operation.
        """
        return await self.send_command("restart", parameter="api-server")

    async def temperature(self) -> dict:
        """Retrieve the current temperature readings from the Auradine miner.

        Returns:
            dict: A dictionary containing temperature data.
        """
        return await self.send_command("temperature")

    async def timedate(self, ntp: str, timezone: str) -> dict:
        """Set the time and date settings for the Auradine miner.

        Args:
            ntp (str): The NTP server to use for time synchronization.
            timezone (str): The timezone setting.

        Returns:
            dict: A dictionary indicating the result of setting the time and date.
        """
        return await self.send_command("timedate", ntp=ntp, timezone=timezone)

    async def get_token(self) -> dict:
        """Retrieve the current authentication token for the Auradine miner.

        Returns:
            dict: A dictionary containing the authentication token.
        """
        return await self.send_command("token", user=self.username, password=self.pwd)

    async def update_pools(self, pools: list[dict]) -> dict:
        """Update the mining pools configuration on the Auradine miner.

        Args:
            pools (list[dict]): A list of dictionaries, each representing a pool configuration.

        Returns:
            dict: A dictionary indicating the result of the update operation.
        """
        return await self.send_command("updatepools", pools=pools)

    async def voltage(self) -> dict:
        """Retrieve the voltage settings of the Auradine miner.

        Returns:
            dict: A dictionary containing the voltage details.
        """
        return await self.send_command("voltage")

    async def get_ztp(self) -> dict:
        """Retrieve the zero-touch provisioning status from the Auradine miner.

        Returns:
            dict: A dictionary containing the ZTP status.
        """
        return await self.send_command("ztp")

    async def set_ztp(self, enable: bool) -> dict:
        """Enable or disable zero-touch provisioning (ZTP) on the Auradine miner.

        Args:
            enable (bool): True to enable ZTP, False to disable.

        Returns:
            dict: A dictionary indicating the result of the ZTP setting operation.
        """
        return await self.send_command("ztp", parameter="on" if enable else "off")
