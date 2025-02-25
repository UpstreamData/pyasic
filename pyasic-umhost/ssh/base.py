import asyncio
import logging
from typing import Optional

import asyncssh


class BaseSSH:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.pwd = None
        self.username = "root"
        self.port = 22

    async def _get_connection(self) -> asyncssh.connect:
        """Create a new asyncssh connection"""
        try:
            conn = await asyncssh.connect(
                str(self.ip),
                port=self.port,
                known_hosts=None,
                username=self.username,
                password=self.pwd,
                server_host_key_algs=["ssh-rsa"],
            )
            return conn
        except asyncssh.misc.PermissionDenied as e:
            raise ConnectionRefusedError from e
        except Exception as e:
            raise ConnectionError from e

    async def send_command(self, cmd: str) -> Optional[str]:
        """Send an ssh command to the miner"""
        try:
            conn = await asyncio.wait_for(self._get_connection(), timeout=10)
        except (ConnectionError, asyncio.TimeoutError):
            return None

        try:
            async with conn:
                resp = await conn.run(cmd)
                result = str(max(resp.stdout, resp.stderr, key=len))

                return result
        except Exception as e:
            logging.error(f"{self} command {cmd} error: {e}")
            return None
