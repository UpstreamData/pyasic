from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from pyasic import APIError, settings
from pyasic.web.base import BaseWebAPI


class ESPMinerWebAPI(BaseWebAPI):
    async def send_command(
        self,
        command: str,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        url = f"http://{self.ip}:{self.port}/api/{command}"
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            retries = settings.get("get_data_retries", 1)
            for attempt in range(retries):
                try:
                    if parameters.get("post", False):
                        parameters.pop("post")
                        data = await client.post(
                            url,
                            timeout=settings.get("api_function_timeout", 3),
                            json=parameters,
                        )
                    elif parameters.get("patch", False):
                        parameters.pop("patch")
                        data = await client.patch(
                            url,
                            timeout=settings.get("api_function_timeout", 3),
                            json=parameters,
                        )
                    else:
                        data = await client.get(
                            url,
                            timeout=settings.get("api_function_timeout", 5),
                        )
                except httpx.HTTPError as e:
                    if attempt == retries - 1:
                        raise APIError(
                            f"HTTP error sending '{command}' to {self.ip}: {e}"
                        )
                else:
                    if data.status_code == 200:
                        try:
                            return data.json()
                        except json.decoder.JSONDecodeError as e:
                            response_text = data.text if data.text else "empty response"
                            if attempt == retries - 1:
                                raise APIError(
                                    f"JSON decode error for '{command}' from {self.ip}: {e} - Response: {response_text}"
                                )
        raise APIError(f"Failed to send command to miner API: {url}")

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        """Execute multiple commands simultaneously on the BitAxe miner.

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

        results = await asyncio.gather(
            *[tasks[cmd] for cmd in tasks], return_exceptions=True
        )

        data: dict[str, Any] = {"multicommand": True}
        for cmd, result in zip(tasks.keys(), results):
            if not isinstance(result, (APIError, Exception)):
                if result is None or result == {}:
                    data[cmd] = {}
                else:
                    data[cmd] = result

        return data

    async def system_info(self) -> dict:
        return await self.send_command("system/info")

    async def swarm_info(self) -> dict:
        return await self.send_command("swarm/info")

    async def restart(self) -> dict:
        return await self.send_command("system/restart", post=True)

    async def update_settings(self, **config: Any) -> dict:
        return await self.send_command("system", patch=True, **config)

    async def asic_info(self) -> dict:
        return await self.send_command("system/asic")
