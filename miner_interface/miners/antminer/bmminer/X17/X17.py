from miner_interface.miners._backends import BMMiner  # noqa - Ignore access to _module

import httpx


class BMMinerX17(BMMiner):
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
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, data={"action": "startBlink"}, auth=auth)
            except httpx.ReadTimeout:
                # Expected behaviour
                pass
            data = await client.post(url, data={"action": "onPageLoaded"}, auth=auth)
        if data.status_code == 200:
            data = data.json()
            if data["isBlinking"]:
                return True
        return False

    async def fault_light_off(self) -> bool:
        url = f"http://{self.ip}/cgi-bin/blink.cgi"
        auth = httpx.DigestAuth("root", "root")
        async with httpx.AsyncClient() as client:
            await client.post(url, data={"action": "stopBlink"}, auth=auth)
            data = await client.post(url, data={"action": "onPageLoaded"}, auth=auth)
        if data.status_code == 200:
            data = data.json()
            if not data["isBlinking"]:
                return True
        return False

    async def check_light(self):
        url = f"http://{self.ip}/cgi-bin/blink.cgi"
        auth = httpx.DigestAuth("root", "root")
        async with httpx.AsyncClient() as client:
            data = await client.post(url, data={"action": "onPageLoaded"}, auth=auth)
        if data.status_code == 200:
            data = data.json()
            if data["isBlinking"]:
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
