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

from typing import List, Optional, Union

from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard
from pyasic.errors import APIError
from pyasic.miners.zec._backends import CGMiner  # noqa - Ignore access to _module
from pyasic.web.X15 import X15WebAPI


class X15(CGMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        self.ip = ip
        self.web = X15WebAPI(ip)

    async def get_config(self) -> MinerConfig:
        data = await self.web.get_miner_conf()
        if data:
            self.config = MinerConfig().from_raw(data)
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        await self.web.set_miner_conf(config.as_x15(user_suffix=user_suffix))

    async def get_mac(self) -> Union[str, None]:
        try:
            data = await self.web.get_system_info()
            if data:
                return data["macaddr"]
        except KeyError:
            pass

    async def fault_light_on(self) -> bool:
        # this should time out, after it does do a check
        await self.web.blink(blink=True)
        try:
            data = await self.web.get_blink_status()
            if data:
                if data["isBlinking"]:
                    self.light = True
        except KeyError:
            pass
        return self.light

    async def fault_light_off(self) -> bool:
        await self.web.blink(blink=False)
        try:
            data = await self.web.get_blink_status()
            if data:
                if not data["isBlinking"]:
                    self.light = False
        except KeyError:
            pass
        return self.light

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            return True
        return False

    async def get_fault_light(self, web_get_blink_status: dict = None) -> bool:
        if self.light:
            return self.light

        if not web_get_blink_status:
            try:
                web_get_blink_status = await self.web.get_blink_status()
            except APIError:
                pass

        if web_get_blink_status:
            try:
                self.light = web_get_blink_status["isBlinking"]
            except KeyError:
                pass
        return self.light

    async def get_hostname(self, web_get_system_info: dict = None) -> Optional[str]:
        if not web_get_system_info:
            try:
                web_get_system_info = await self.web.get_system_info()
            except APIError:
                pass

        if web_get_system_info:
            try:
                return web_get_system_info["hostname"]
            except KeyError:
                pass

    async def get_model(self, web_get_system_info: dict = None) -> Optional[str]:
        if self.model:
            return self.model

        if not web_get_system_info:
            try:
                web_get_system_info = await self.web.get_system_info()
            except APIError:
                pass

        if web_get_system_info:
            try:
                return web_get_system_info["minertype"]
            except APIError:
                pass

    async def get_fans(self, api_stats: dict = None) -> List[Fan]:
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        fans_data = [Fan(), Fan(), Fan(), Fan()]
        if api_stats:
            try:
                fan_offset = -1

                for fan_num in range(1, 8, 4):
                    for _f_num in range(4):
                        f = api_stats["STATS"][1].get(f"fan{fan_num + _f_num}")
                        if f and not f == 0 and fan_offset == -1:
                            fan_offset = fan_num + 2
                if fan_offset == -1:
                    fan_offset = 3

                for fan in range(self.fan_count):
                    fans_data[fan] = Fan(
                        api_stats["STATS"][1].get(f"fan{fan_offset+fan}")
                    )
            except (KeyError, IndexError):
                pass
        return fans_data

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
                            hashboard.hashrate = round(float(hashrate), 2)

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
