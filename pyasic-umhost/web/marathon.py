from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from pyasic import settings
from pyasic.web.base import BaseWebAPI


class MaraWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            tasks = [
                asyncio.create_task(self._handle_multicommand(client, command))
                for command in commands
            ]
            all_data = await asyncio.gather(*tasks)

        data = {}
        for item in all_data:
            data.update(item)

        data["multicommand"] = True
        return data

    async def _handle_multicommand(
        self, client: httpx.AsyncClient, command: str
    ) -> dict:
        auth = httpx.DigestAuth(self.username, self.pwd)

        try:
            url = f"http://{self.ip}:{self.port}/kaonsu/v1/{command}"
            ret = await client.get(url, auth=auth)
        except httpx.HTTPError:
            pass
        else:
            if ret.status_code == 200:
                try:
                    json_data = ret.json()
                    return {command: json_data}
                except json.decoder.JSONDecodeError:
                    pass
        return {command: {}}

    async def send_command(
        self,
        command: str | bytes,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        url = f"http://{self.ip}:{self.port}/kaonsu/v1/{command}"
        auth = httpx.DigestAuth(self.username, self.pwd)
        try:
            async with httpx.AsyncClient(
                transport=settings.transport(),
            ) as client:
                if parameters:
                    data = await client.post(
                        url,
                        auth=auth,
                        timeout=settings.get("api_function_timeout", 3),
                        json=parameters,
                    )
                else:
                    data = await client.get(url, auth=auth)
        except httpx.HTTPError:
            pass
        else:
            if data.status_code == 200:
                try:
                    return data.json()
                except json.decoder.JSONDecodeError:
                    pass

    async def brief(self):
        return await self.send_command("brief")

    async def ping(self):
        return await self.send_command("ping")

    async def get_locate_miner(self):
        return await self.send_command("locate_miner")

    async def set_locate_miner(self, blinking: bool):
        return await self.send_command("locate_miner", blinking=blinking)

    async def reboot(self):
        return await self.send_command("maintenance", type="reboot")

    async def reset(self):
        return await self.send_command("maintenance", type="reset")

    async def reload(self):
        return await self.send_command("maintenance", type="reload")

    async def set_password(self, new_pwd: str):
        return await self.send_command(
            "maintenance",
            type="passwd",
            params={"curPwd": self.pwd, "confirmPwd": self.pwd, "newPwd": new_pwd},
        )

    async def get_network_config(self):
        return await self.send_command("network_config")

    async def set_network_config(self, **params):
        return await self.send_command("network_config", **params)

    async def get_miner_config(self):
        return await self.send_command("miner_config")

    async def set_miner_config(self, **params):
        return await self.send_command("miner_config", **params)

    async def fans(self):
        return await self.send_command("fans")

    async def log(self):
        return await self.send_command("log")

    async def overview(self):
        return await self.send_command("overview")

    async def connections(self):
        return await self.send_command("connections")

    async def controlboard_info(self):
        return await self.send_command("controlboard_info")

    async def event_chart(self):
        return await self.send_command("event_chart")

    async def hashboards(self):
        return await self.send_command("hashboards")

    async def pools(self):
        return await self.send_command("pools")
