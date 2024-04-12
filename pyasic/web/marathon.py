from __future__ import annotations

import json
from typing import Any

import httpx

from pyasic import settings
from pyasic.web.antminer import AntminerModernWebAPI


class MaraWebAPI(AntminerModernWebAPI):
    def __init__(self, ip: str) -> None:
        self.am_commands = [
            "get_miner_conf",
            "set_miner_conf",
            "blink",
            "reboot",
            "get_system_info",
            "get_network_info",
            "summary",
            "get_blink_status",
            "set_network_conf",
        ]
        super().__init__(ip)

    async def _send_mara_command(
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

    async def _send_am_command(
        self,
        command: str | bytes,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ):
        url = f"http://{self.ip}:{self.port}/cgi-bin/{command}.cgi"
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

    async def send_command(
        self,
        command: str | bytes,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        if command in self.am_commands:
            return await self._send_am_command(
                command,
                ignore_errors=ignore_errors,
                allow_warning=allow_warning,
                privileged=privileged,
                **parameters,
            )
        return await self._send_mara_command(
            command,
            ignore_errors=ignore_errors,
            allow_warning=allow_warning,
            privileged=privileged,
            **parameters,
        )

    async def brief(self):
        return await self.send_command("brief")

    async def overview(self):
        return await self.send_command("overview")

    async def connections(self):
        return await self.send_command("connections")

    async def event_chart(self):
        return await self.send_command("event_chart")

    async def hashboards(self):
        return await self.send_command("hashboards")

    async def mara_pools(self):
        return await self._send_mara_command("pools")
