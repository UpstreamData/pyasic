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
from pyasic.data import HashBoard
from pyasic.data.error_codes import MinerErrorData, X19Error
from pyasic.miners.btc._backends import BMMiner  # noqa - Ignore access to _module
from pyasic.web.X7 import X7WebAPI


class X7(BMMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        self.ip = ip
        self.web = X7WebAPI(ip)

    async def get_config(self) -> MinerConfig:
        data = await self.web.get_miner_conf()
        if data:
            self.config = MinerConfig().from_raw(data)
        return self.config

    async def get_hashrate(self, api_summary: dict = None) -> Optional[float]:
        # get hr from API
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                # not actually GHS, MHS.
                return round(float(api_summary["SUMMARY"][0]["GHS 5s"] / 1000000), 5)
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def get_hashboards(self, api_stats: dict = None) -> List[HashBoard]:
        hashboards = []

        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            try:
                board_offset = -1
                boards = api_stats["STATS"]
                if len(boards) > 1:
                    for board_num in range(1, 16, 5):
                        for _b_num in range(5):
                            b = boards[1].get(f"chain_acn{board_num + _b_num}")

                            if b and not b == 0 and board_offset == -1:
                                board_offset = board_num
                    if board_offset == -1:
                        board_offset = 1

                    for i in range(board_offset, board_offset + self.ideal_hashboards):
                        hashboard = HashBoard(
                            slot=i - board_offset, expected_chips=self.nominal_chips
                        )

                        chip_temp = boards[1].get(f"temp{i}")
                        if chip_temp:
                            hashboard.chip_temp = round(chip_temp)

                        temp = boards[1].get(f"temp2_{i}")
                        if temp:
                            hashboard.temp = round(temp)

                        hashrate = boards[1].get(f"chain_rate{i}")
                        if hashrate:
                            hashboard.hashrate = round(float(hashrate) / 1000, 5)

                        chips = boards[1].get(f"chain_acn{i}")
                        if chips:
                            hashboard.chips = chips
                            hashboard.missing = False
                        if (not chips) or (not chips > 0):
                            hashboard.missing = True
                        hashboards.append(hashboard)
            except (IndexError, KeyError, ValueError, TypeError):
                pass

        return hashboards

    async def get_nominal_hashrate(self, api_stats: dict = None) -> Optional[float]:
        # X19 method, not sure compatibility
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
                    rate_unit = "MH"
                if rate_unit == "GH":
                    return round(ideal_rate, 2)
                if rate_unit == "MH":
                    return round(ideal_rate / 1000000, 5)
                else:
                    return round(ideal_rate, 2)
            except (KeyError, IndexError):
                pass

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
