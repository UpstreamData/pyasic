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

import ipaddress
import logging
from typing import List, Union, Tuple, Optional
from collections import namedtuple

import asyncssh

from pyasic.API.bmminer import BMMinerAPI
from pyasic.config import MinerConfig
from pyasic.data import HashBoard, MinerData
from pyasic.data.error_codes import MinerErrorData
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner
from pyasic.settings import PyasicSettings


class BMMiner(BaseMiner):
    """Base handler for BMMiner based miners."""

    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = BMMinerAPI(ip, api_ver)
        self.api_type = "BMMiner"
        self.api_ver = api_ver
        self.uname = "root"
        self.pwd = "admin"

    async def send_ssh_command(self, cmd: str) -> Optional[str]:
        result = None

        try:
            conn = await self._get_ssh_connection()
        except asyncssh.Error:
            return None

        # open an ssh connection
        async with conn:
            # 3 retries
            for i in range(3):
                try:
                    # run the command and get the result
                    result = await conn.run(cmd)
                    result = result.stdout

                except Exception as e:
                    # if the command fails, log it
                    logging.warning(f"{self} command {cmd} error: {e}")

                    # on the 3rd retry, return None
                    if i == 3:
                        return
                    continue
        # return the result, either command output or None
        return result

    async def get_config(self) -> MinerConfig:
        # get pool data
        try:
            pools = await self.api.pools()
        except APIError:
            return self.config

        self.config = MinerConfig().from_api(pools["POOLS"])
        return self.config

    async def reboot(self) -> bool:
        logging.debug(f"{self}: Sending reboot command.")
        _ret = await self.send_ssh_command("reboot")
        logging.debug(f"{self}: Reboot command completed.")
        if isinstance(_ret, str):
            return True
        return False

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        return None

    async def fault_light_off(self) -> bool:
        return False

    async def fault_light_on(self) -> bool:
        return False

    async def restart_backend(self) -> bool:
        return False

    async def stop_mining(self) -> bool:
        return False

    async def resume_mining(self) -> bool:
        return False

    async def set_power_limit(self, wattage: int) -> bool:
        return False

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(self) -> str:
        return "00:00:00:00:00:00"

    async def get_model(self, api_devdetails: dict = None) -> Optional[str]:
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model

        if not api_devdetails:
            try:
                api_devdetails = await self.api.devdetails()
            except APIError:
                pass

        if api_devdetails:
            try:
                self.model = api_devdetails["DEVDETAILS"][0]["Model"].replace(
                    "Antminer ", ""
                )
                logging.debug(f"Found model for {self.ip}: {self.model}")
                return self.model
            except (TypeError, IndexError, KeyError):
                pass

        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def get_version(
        self, api_version: dict = None
    ) -> Tuple[Optional[str], Optional[str]]:
        miner_version = namedtuple("MinerVersion", "api_ver fw_ver")
        # Check to see if the version info is already cached
        if self.api_ver and self.fw_ver:
            return miner_version(self.api_ver, self.fw_ver)

        if not api_version:
            try:
                api_version = await self.api.version()
            except APIError:
                pass

        if api_version:
            try:
                self.api_ver = api_version["VERSION"][0]["API"]
            except (KeyError, IndexError):
                pass
            try:
                self.fw_ver = api_version["VERSION"][0]["CompileTime"]
            except (KeyError, IndexError):
                pass

        return miner_version(self.api_ver, self.fw_ver)

    async def get_hostname(self) -> Optional[str]:
        hn = await self.send_ssh_command("cat /proc/sys/kernel/hostname")
        if hn:
            self.hostname = hn
        return self.hostname

    async def get_hashrate(self, api_summary: dict = None) -> Optional[float]:
        # get hr from API
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return round(float(api_summary["SUMMARY"][0]["GHS 5s"] / 1000), 2)
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
                            hashboard.hashrate = round(float(hashrate) / 1000, 2)

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

    async def get_env_temp(self) -> Optional[float]:
        return None

    async def get_wattage(self) -> Optional[int]:
        return None

    async def get_wattage_limit(self) -> Optional[int]:
        return None

    async def get_fans(
        self, api_stats: dict = None
    ) -> Tuple[
        Tuple[Optional[int], Optional[int], Optional[int], Optional[int]],
        Tuple[Optional[int]],
    ]:
        fan_speeds = namedtuple("FanSpeeds", "fan_1 fan_2 fan_3 fan_4")
        psu_fan_speeds = namedtuple("PSUFanSpeeds", "psu_fan")
        miner_fan_speeds = namedtuple("MinerFans", "fan_speeds psu_fan_speeds")

        psu_fans = psu_fan_speeds(None)

        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        fans_data = [None, None, None, None]
        if api_stats:
            try:
                fan_offset = -1

                for fan_num in range(1, 8, 4):
                    for _f_num in range(4):
                        f = api_stats["STATS"][1].get(f"fan{fan_num + _f_num}")
                        if f and not f == 0 and fan_offset == -1:
                            fan_offset = fan_num
                if fan_offset == -1:
                    fan_offset = 1

                for fan in range(self.fan_count):
                    fans_data[fan] = api_stats["STATS"][1].get(f"fan{fan_offset+fan}")
            except (KeyError, IndexError):
                pass
        fans = fan_speeds(*fans_data)

        return miner_fan_speeds(fans, psu_fans)

    async def get_pools(self, api_pools: dict = None) -> List[dict]:
        groups = []

        if not api_pools:
            try:
                api_pools = await self.api.pools()
            except APIError:
                pass

        if api_pools:
            try:
                pools = {}
                for i, pool in enumerate(api_pools["POOLS"]):
                    pools[f"pool_{i + 1}_url"] = (
                        pool["URL"]
                        .replace("stratum+tcp://", "")
                        .replace("stratum2+tcp://", "")
                    )
                    pools[f"pool_{i + 1}_user"] = pool["User"]
                    pools["quota"] = pool["Quota"] if pool.get("Quota") else "0"

                groups.append(pools)
            except KeyError:
                pass
        return groups

    async def get_errors(self) -> List[MinerErrorData]:
        return []

    async def get_fault_light(self) -> bool:
        return False

    async def _get_data(self, allow_warning: bool) -> dict:
        miner_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            try:
                miner_data = await self.api.multicommand(
                    "summary",
                    "pools",
                    "version",
                    "devdetails",
                    "stats",
                    allow_warning=allow_warning,
                )
            except APIError:
                try:
                    miner_data = await self.api.multicommand(
                        "summary",
                        "version",
                        "pools",
                        "stats",
                        allow_warning=allow_warning,
                    )
                except APIError:
                    pass
            if miner_data:
                break
        if miner_data:
            summary = miner_data.get("summary")
            if summary:
                summary = summary[0]
            pools = miner_data.get("pools")
            if pools:
                pools = pools[0]
            version = miner_data.get("version")
            if version:
                version = version[0]
            devdetails = miner_data.get("devdetails")
            if devdetails:
                devdetails = devdetails[0]
            stats = miner_data.get("stats")
            if stats:
                stats = stats[0]
        else:
            summary, pools, devdetails, version, stats = (None for _ in range(5))

        data = {  # noqa - Ignore dictionary could be re-written
            # ip - Done at start
            # datetime - Done auto
            "mac": await self.get_mac(),
            "model": await self.get_model(api_devdetails=devdetails),
            # make - Done at start
            # api_ver - Done at end
            # fw_ver - Done at end
            "hostname": await self.get_hostname(),
            "hashrate": await self.get_hashrate(api_summary=summary),
            "hashboards": await self.get_hashboards(api_stats=stats),
            # ideal_hashboards - Done at start
            "env_temp": await self.get_env_temp(),
            "wattage": await self.get_wattage(),
            "wattage_limit": await self.get_wattage_limit(),
            # fan_1 - Done at end
            # fan_2 - Done at end
            # fan_3 - Done at end
            # fan_4 - Done at end
            # fan_psu - Done at end
            # ideal_chips - Done at start
            # pool_split - Done at end
            # pool_1_url - Done at end
            # pool_1_user - Done at end
            # pool_2_url - Done at end
            # pool_2_user - Done at end
            "errors": await self.get_errors(),
            "fault_light": await self.get_fault_light(),
        }

        data["api_ver"], data["fw_ver"] = await self.get_version(api_version=version)
        fan_data = await self.get_fans()

        data["fan_1"] = fan_data.fan_speeds.fan_1  # noqa
        data["fan_2"] = fan_data.fan_speeds.fan_2  # noqa
        data["fan_3"] = fan_data.fan_speeds.fan_3  # noqa
        data["fan_4"] = fan_data.fan_speeds.fan_4  # noqa

        data["fan_psu"] = fan_data.psu_fan_speeds.psu_fan  # noqa

        pools_data = await self.get_pools(api_pools=pools)
        data["pool_1_url"] = pools_data[0]["pool_1_url"]
        data["pool_1_user"] = pools_data[0]["pool_1_user"]
        if len(pools_data) > 1:
            data["pool_2_url"] = pools_data[1]["pool_1_url"]
            data["pool_2_user"] = pools_data[1]["pool_1_user"]
            data["pool_split"] = f"{pools_data[0]['quota']}/{pools_data[1]['quota']}"
        else:
            try:
                data["pool_2_url"] = pools_data[0]["pool_1_url"]
                data["pool_2_user"] = pools_data[0]["pool_1_user"]
                data["quota"] = "0"
            except KeyError:
                pass

        return data
