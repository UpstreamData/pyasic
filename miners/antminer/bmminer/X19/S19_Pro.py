from miners._backends import BMMiner  # noqa - Ignore access to _module
from miners._types import S19Pro  # noqa - Ignore access to _module

from config.miner_config import MinerConfig

import httpx
import json
import asyncio


class BMMinerS19Pro(BMMiner, S19Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def get_config(self) -> MinerConfig:
        url = f"http://{self.ip}/cgi-bin/get_miner_conf.cgi"
        auth = httpx.DigestAuth("root", "root")
        async with httpx.AsyncClient() as client:
            data = await client.get(url, auth=auth)
        if data.status_code == 200:
            data = data.json()
            self.config = MinerConfig().from_raw(data)
        return self.config

    async def send_config(self, yaml_config, ip_user: bool = False) -> None:
        url = f"http://{self.ip}/cgi-bin/set_miner_conf.cgi"
        auth = httpx.DigestAuth("root", "root")
        if ip_user:
            suffix = str(self.ip).split(".")[-1]
            conf = MinerConfig().from_yaml(yaml_config).as_x19(user_suffix=suffix)
        else:
            conf = MinerConfig().from_yaml(yaml_config).as_x19()

        try:
            async with httpx.AsyncClient() as client:
                await client.post(url, data=conf, auth=auth)
        except httpx.ReadTimeout:
            pass
        for i in range(7):
            data = await self.get_config()
            if data.as_x19() == conf:
                break
            await asyncio.sleep(1)

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

    async def get_mac(self):
        mac = None
        url = f"http://{self.ip}/cgi-bin/get_system_info.cgi"
        auth = httpx.DigestAuth("root", "root")
        async with httpx.AsyncClient() as client:
            data = await client.get(url, auth=auth)
        if data.status_code == 200:
            data = data.json()
            if len(data.keys()) > 0:
                if "macaddr" in data.keys():
                    mac = data["macaddr"]
        return mac

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

    async def reboot(self) -> bool:
        url = f"http://{self.ip}/cgi-bin/reboot.cgi"
        auth = httpx.DigestAuth("root", "root")
        async with httpx.AsyncClient() as client:
            data = await client.get(url, auth=auth)
        if data.status_code == 200:
            return True
        return False
