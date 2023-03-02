# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------

import asyncio
from typing import List, Optional, Union

from pyasic.API import APIError
from pyasic.config import MinerConfig, X19PowerMode
from pyasic.data.error_codes import MinerErrorData, X19Error
from pyasic.miners.btc._backends import BMMiner  # noqa - Ignore access to _module
from pyasic.web.X19 import X19WebAPI


class X19(BMMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        self.ip = ip
        self.web = X19WebAPI(ip)

    async def get_config(self) -> MinerConfig:
        data = await self.web.get_miner_conf()
        if data:
            self.config = MinerConfig().from_raw(data)
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config
        conf = config.as_x19(user_suffix=user_suffix)
        await self.web.set_miner_conf(conf)

        for i in range(7):
            data = await self.get_config()
            if data.as_x19() == conf:
                break
            await asyncio.sleep(1)

    async def fault_light_on(self) -> bool:
        data = await self.web.blink(blink=True)
        if data:
            if data.get("code") == "B000":
                self.light = True
        return self.light

    async def fault_light_off(self) -> bool:
        data = await self.web.blink(blink=False)
        if data:
            if data.get("code") == "B100":
                self.light = True
        return self.light

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            return True
        return False

    async def stop_mining(self) -> bool:
        cfg = await self.get_config()
        cfg.miner_mode = X19PowerMode.Sleep
        await self.send_config(cfg)
        return True

    async def resume_mining(self) -> bool:
        cfg = await self.get_config()
        cfg.miner_mode = X19PowerMode.Normal
        await self.send_config(cfg)
        return True

    async def get_hostname(self) -> Union[str, None]:
        try:
            data = await self.web.get_system_info()
            if data:
                return data["hostname"]
        except KeyError:
            pass

    async def get_mac(self) -> Union[str, None]:
        try:
            data = await self.web.get_system_info()
            if data:
                return data["macaddr"]
        except KeyError:
            pass

        try:
            data = await self.web.get_network_info()
            if data:
                return data["macaddr"]
        except KeyError:
            pass

    async def get_errors(self) -> List[MinerErrorData]:
        errors = []
        data = await self.web.summary()
        if data:
            try:
                for item in data["SUMMARY"][0]["status"]:
                    try:
                        if not item["status"] == "s":
                            errors.append(X19Error(item["msg"]))
                    except KeyError:
                        continue
            except (KeyError, IndexError):
                pass
        return errors

    async def get_fault_light(self) -> bool:
        if self.light:
            return self.light
        try:
            data = await self.web.get_blink_status()
            if data:
                self.light = data["blink"]
        except KeyError:
            pass
        return self.light

    async def get_nominal_hashrate(self, api_stats: dict = None) -> Optional[float]:
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            try:
                ideal_rate = api_stats["STATS"][1]["total_rateideal"]
                try:
                    rate_unit = api_stats["STATS"][1]["rate_unit"]
                except KeyError:
                    rate_unit = "GH"
                if rate_unit == "GH":
                    return round(ideal_rate / 1000, 2)
                if rate_unit == "MH":
                    return round(ideal_rate / 1000000, 2)
                else:
                    return round(ideal_rate, 2)
            except (KeyError, IndexError):
                pass

    async def set_static_ip(
        self,
        ip: str,
        dns: str,
        gateway: str,
        subnet_mask: str = "255.255.255.0",
        hostname: str = None,
    ):
        if not hostname:
            hostname = await self.get_hostname()
        await self.web.set_network_conf(
            ip=ip,
            dns=dns,
            gateway=gateway,
            subnet_mask=subnet_mask,
            hostname=hostname,
            protocol=2,
        )

    async def set_dhcp(self, hostname: str = None):
        if not hostname:
            hostname = await self.get_hostname()
        await self.web.set_network_conf(
            ip="", dns="", gateway="", subnet_mask="", hostname=hostname, protocol=1
        )

    async def set_hostname(self, hostname: str):
        cfg = await self.web.get_network_info()
        dns = cfg["conf_dnsservers"]
        gateway = cfg["conf_gateway"]
        ip = cfg["conf_ipaddress"]
        subnet_mask = cfg["conf_netmask"]
        protocol = 1 if cfg["conf_nettype"] == "DHCP" else 2
        await self.web.set_network_conf(
            ip=ip,
            dns=dns,
            gateway=gateway,
            subnet_mask=subnet_mask,
            hostname=hostname,
            protocol=protocol,
        )
