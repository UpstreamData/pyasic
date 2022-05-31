from miners._backends import BMMiner  # noqa - Ignore access to _module
from miners._types import S19  # noqa - Ignore access to _module

import httpx
import json


class BMMinerS19(BMMiner, S19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def get_hostname(self) -> str or None:
        hostname = None
        url = f"http://{self.ip}/cgi-bin/get_system_info.cgi"
        auth = httpx.DigestAuth("root", "root")
        async with httpx.AsyncClient() as client:
            data = await client.get(url, auth=auth)
        if data.status_code == 200:
            data = data.json()
            if len(data.keys()) > 0:
                if "hostname" in data.keys():
                    hostname = data["hostname"]
        return hostname

    async def fault_light_on(self) -> bool:
        url = f"http://{self.ip}/cgi-bin/blink.cgi"
        auth = httpx.DigestAuth("root", "root")
        data = json.dumps({"blink": "true"})
        async with httpx.AsyncClient() as client:
            data = await client.post(url, data=data, auth=auth)
        if data.status_code == 200:
            data = data.json()
            if data.get("code") == "B000":
                return True
        return False

    async def fault_light_off(self) -> bool:
        url = f"http://{self.ip}/cgi-bin/blink.cgi"
        auth = httpx.DigestAuth("root", "root")
        data = json.dumps({"blink": "false"})
        async with httpx.AsyncClient() as client:
            data = await client.post(url, data=data, auth=auth)
        if data.status_code == 200:
            data = data.json()
            if data.get("code") == "B100":
                return True
        return False
