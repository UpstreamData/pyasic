#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from pyasic.miners._backends import BMMiner  # noqa - Ignore access to _module

from pyasic.config import MinerConfig
from pyasic.data.error_codes import X19Error, MinerErrorData
from pyasic.settings import PyasicSettings

import httpx
import json
import asyncio
from typing import Union, List


class BMMinerX19(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
        self.uname = "root"
        self.pwd = PyasicSettings().global_x19_password

    async def check_light(self) -> Union[bool, None]:
        if self.light:
            return self.light
        url = f"http://{self.ip}/cgi-bin/get_blink_status.cgi"
        auth = httpx.DigestAuth(self.uname, self.pwd)
        async with httpx.AsyncClient() as client:
            data = await client.get(url, auth=auth)
        if data.status_code == 200:
            data = data.json()
            light = data["blink"]
            self.light = light
            return light
        return None

    async def get_config(self) -> MinerConfig:
        url = f"http://{self.ip}/cgi-bin/get_miner_conf.cgi"
        auth = httpx.DigestAuth(self.uname, self.pwd)
        async with httpx.AsyncClient() as client:
            data = await client.get(url, auth=auth)
        if data.status_code == 200:
            data = data.json()
            self.config = MinerConfig().from_raw(data)
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        url = f"http://{self.ip}/cgi-bin/set_miner_conf.cgi"
        auth = httpx.DigestAuth(self.uname, self.pwd)
        conf = config.as_x19(user_suffix=user_suffix)

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

    async def get_hostname(self) -> Union[str, None]:
        hostname = None
        url = f"http://{self.ip}/cgi-bin/get_system_info.cgi"
        auth = httpx.DigestAuth(self.uname, self.pwd)
        async with httpx.AsyncClient() as client:
            data = await client.get(url, auth=auth)
        if data.status_code == 200:
            data = data.json()
            if len(data.keys()) > 0:
                if "hostname" in data.keys():
                    hostname = data["hostname"]
        return hostname

    async def get_mac(self) -> Union[str, None]:
        mac = None
        url = f"http://{self.ip}/cgi-bin/get_system_info.cgi"
        auth = httpx.DigestAuth(self.uname, self.pwd)
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
        auth = httpx.DigestAuth(self.uname, self.pwd)
        data = json.dumps({"blink": "true"})
        async with httpx.AsyncClient() as client:
            data = await client.post(url, data=data, auth=auth)
        if data.status_code == 200:
            data = data.json()
            if data.get("code") == "B000":
                self.light = True
                return True
        return False

    async def fault_light_off(self) -> bool:
        url = f"http://{self.ip}/cgi-bin/blink.cgi"
        auth = httpx.DigestAuth(self.uname, self.pwd)
        data = json.dumps({"blink": "false"})
        async with httpx.AsyncClient() as client:
            data = await client.post(url, data=data, auth=auth)
        if data.status_code == 200:
            data = data.json()
            if data.get("code") == "B100":
                self.light = False
                return True
        return False

    async def reboot(self) -> bool:
        url = f"http://{self.ip}/cgi-bin/reboot.cgi"
        auth = httpx.DigestAuth(self.uname, self.pwd)
        async with httpx.AsyncClient() as client:
            data = await client.get(url, auth=auth)
        if data.status_code == 200:
            return True
        return False

    async def get_errors(self) -> List[MinerErrorData]:
        errors = []
        url = f"http://{self.ip}/cgi-bin/summary.cgi"
        auth = httpx.DigestAuth(self.uname, self.pwd)
        async with httpx.AsyncClient() as client:
            data = await client.get(url, auth=auth)
        if data:
            data = data.json()
            if "SUMMARY" in data.keys():
                if "status" in data["SUMMARY"][0].keys():
                    for item in data["SUMMARY"][0]["status"]:
                        if not item["status"] == "s":
                            errors.append(X19Error(item["msg"]))
        return errors

    async def stop_mining(self) -> bool:
        cfg = await self.get_config()
        cfg.autotuning_wattage = 0
        await self.send_config(cfg)
        return True

    async def resume_mining(self) -> bool:
        cfg = await self.get_config()
        cfg.autotuning_wattage = 1
        await self.send_config(cfg)
        return True
