from miners._backends import BMMiner  # noqa - Ignore access to _module
from miners._types import T19  # noqa - Ignore access to _module

import httpx
import json


class BMMinerT19(BMMiner, T19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def get_hostname(self) -> str:
        return "?"

    async def fault_light_on(self) -> bool:
        url = f"http://{self.ip}/cgi-bin/blink.cgi"
        auth = httpx.DigestAuth("root", "root")
        data = json.dumps({"blink": "true"})
        async with httpx.AsyncClient() as client:
            data = await client.post(url, data=data, auth=auth)
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
        data = data.json()
        if data.get("code") == "B100":
            return True
        return False
