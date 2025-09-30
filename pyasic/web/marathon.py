from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from pyasic import settings
from pyasic.errors import APIError
from pyasic.web.base import BaseWebAPI


class MaraWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.username: str = "root"
        self.pwd: str = "root"

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
        auth = httpx.DigestAuth(self.username, self.pwd)

        try:
            url = f"http://{self.ip}:{self.port}/kaonsu/v1/{command}"
            ret = await client.get(url, auth=auth)
        except httpx.HTTPError:
            pass
        else:
            if ret.status_code == 200:
                try:
                    json_data: dict[str, Any] = ret.json()
                    return {command: json_data}
                except json.decoder.JSONDecodeError:
                    pass
        return {command: {}}

    async def send_command(
        self,
        command: str,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        url = f"http://{self.ip}:{self.port}/kaonsu/v1/{command}"
        auth = httpx.DigestAuth(self.username, self.pwd)
        try:
            async with httpx.AsyncClient(
                transport=settings.transport(),
            ) as client:
                if parameters:
                    response = await client.post(
                        url,
                        auth=auth,
                        timeout=settings.get("api_function_timeout", 3),
                        json=parameters,
                    )
                else:
                    response = await client.get(url, auth=auth)
        except httpx.HTTPError:
            pass
        else:
            if response.status_code == 200:
                try:
                    result: dict[str, Any] = response.json()
                    return result
                except json.decoder.JSONDecodeError as e:
                    response_text = response.text if response.text else "empty response"
                    raise APIError(
                        f"JSON decode error for '{command}' from {self.ip}: {e} - Response: {response_text}"
                    )
        raise APIError(f"Failed to send command to miner API: {url}")

    async def brief(self) -> dict[str, Any]:
        return await self.send_command("brief")

    async def ping(self) -> dict[str, Any]:
        return await self.send_command("ping")

    async def get_locate_miner(self) -> dict[str, Any]:
        return await self.send_command("locate_miner")

    async def set_locate_miner(self, blinking: bool) -> dict[str, Any]:
        return await self.send_command("locate_miner", blinking=blinking)

    async def reboot(self) -> dict[str, Any]:
        return await self.send_command("maintenance", type="reboot")

    async def reset(self) -> dict[str, Any]:
        return await self.send_command("maintenance", type="reset")

    async def reload(self) -> dict[str, Any]:
        return await self.send_command("maintenance", type="reload")

    async def set_password(self, new_pwd: str) -> dict[str, Any]:
        return await self.send_command(
            "maintenance",
            type="passwd",
            params={"curPwd": self.pwd, "confirmPwd": self.pwd, "newPwd": new_pwd},
        )

    async def get_network_config(self) -> dict[str, Any]:
        return await self.send_command("network_config")

    async def set_network_config(self, **params: Any) -> dict[str, Any]:
        return await self.send_command("network_config", **params)

    async def get_miner_config(self) -> dict[str, Any]:
        return await self.send_command("miner_config")

    async def set_miner_config(self, **params: Any) -> dict[str, Any]:
        return await self.send_command("miner_config", **params)

    async def fans(self) -> dict[str, Any]:
        return await self.send_command("fans")

    async def log(self) -> dict[str, Any]:
        return await self.send_command("log")

    async def overview(self) -> dict[str, Any]:
        return await self.send_command("overview")

    async def connections(self) -> dict[str, Any]:
        return await self.send_command("connections")

    async def controlboard_info(self) -> dict[str, Any]:
        return await self.send_command("controlboard_info")

    async def event_chart(self) -> dict[str, Any]:
        return await self.send_command("event_chart")

    async def hashboards(self) -> dict[str, Any]:
        return await self.send_command("hashboards")

    async def pools(self) -> dict[str, Any]:
        return await self.send_command("pools")
