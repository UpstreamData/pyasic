from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from pyasic import APIError, settings
from pyasic.web.base import BaseWebAPI


class BitAxeWebAPI(BaseWebAPI):
    async def send_command(
        self,
        command: str | bytes,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        url = f"http://{self.ip}:{self.port}/api/{command}"
        try:
            async with httpx.AsyncClient(
                transport=settings.transport(),
            ) as client:
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
                    data = await client.get(url)
        except httpx.HTTPError:
            pass
        else:
            if data.status_code == 200:
                try:
                    return data.json()
                except json.decoder.JSONDecodeError:
                    pass

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

    async def system_info(self):
        return await self.send_command("system/info")

    async def swarm_info(self):
        return await self.send_command("swarm/info")

    async def restart(self):
        return await self.send_command("system/restart", post=True)

    async def update_settings(self, **config):
        return await self.send_command("system", patch=True, **config)
