"""Web API client for Fluminer stock firmware."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.parse import urlsplit

import httpx

from pyasic import settings
from pyasic.errors import APIError
from pyasic.web.base import BaseWebAPI


class FluminerWebAPI(BaseWebAPI):
    def __init__(self, ip: str) -> None:
        """Initialize the web API client and parse optional host ports."""
        super().__init__(ip)
        parsed = urlsplit(f"//{ip}")
        if parsed.hostname is not None:
            self.ip = parsed.hostname
        if parsed.port is not None:
            self.port = parsed.port
        self.username = "root"
        self.pwd = settings.get("default_fluminer_web_password", "root")
        self._session_cookie: str | None = None

    async def auth(self) -> str | None:
        """Authenticate with the web UI and cache the session cookie."""
        async with httpx.AsyncClient(transport=settings.transport()) as client:
            try:
                response = await client.post(
                    f"http://{self.ip}:{self.port}/api/login",
                    json={"username": self.username, "password": self.pwd},
                    timeout=settings.get("api_function_timeout", 5),
                )
                data = response.json()
            except (httpx.HTTPError, json.JSONDecodeError):
                return None

            if data.get("code") != 0:
                return None

            session_cookie = response.cookies.get("session")
            self._session_cookie = session_cookie
            return session_cookie

    async def send_command(
        self,
        command: str,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        privileged: bool = False,
        **parameters: Any,
    ) -> dict:
        command = command.lstrip("/")
        url = f"http://{self.ip}:{self.port}/{command}"

        async with httpx.AsyncClient(transport=settings.transport()) as client:
            retries = settings.get("get_data_retries", 1)
            if privileged:
                retries = max(retries, 2)
            for attempt in range(retries):
                if privileged and self._session_cookie is None:
                    await self.auth()
                try:
                    response = await client.get(
                        url,
                        cookies=(
                            {"session": self._session_cookie}
                            if self._session_cookie is not None
                            else None
                        ),
                        timeout=settings.get("api_function_timeout", 5),
                    )
                    data = response.json()
                except (httpx.HTTPError, json.JSONDecodeError):
                    if attempt == retries - 1 and not ignore_errors:
                        raise APIError(f"Failed to send command to miner API: {url}")
                    continue

                if data.get("code") == 401 and privileged and attempt < retries - 1:
                    self._session_cookie = None
                    await self.auth()
                    continue
                if response.status_code == 200 and data.get("code") == 0:
                    return data
                if ignore_errors:
                    return data

        raise APIError(f"Command failed: {command}")

    async def multicommand(
        self, *commands: str, ignore_errors: bool = False, allow_warning: bool = True
    ) -> dict:
        tasks = {
            command: asyncio.create_task(
                self.send_command(
                    command,
                    ignore_errors=ignore_errors,
                    allow_warning=allow_warning,
                    privileged=command == "api/getPools",
                )
            )
            for command in commands
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        data: dict[str, Any] = {"multicommand": True}
        for command, result in zip(tasks.keys(), results):
            if isinstance(result, dict):
                data[command] = result
        return data

    async def overview(self) -> dict:
        """Return miner overview and identity information."""
        return await self.send_command("api/overview")

    async def summary(self) -> dict:
        """Return current mining summary information."""
        return await self.send_command("api/summary")

    async def network(self) -> dict:
        """Return current network configuration information."""
        return await self.send_command("api/getNetwork")

    async def pools(self) -> dict:
        """Return configured pool information."""
        return await self.send_command("api/getPools", privileged=True)
