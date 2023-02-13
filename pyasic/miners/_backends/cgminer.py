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

import ipaddress
import logging
from collections import namedtuple
from typing import List, Optional, Tuple, Union

import asyncssh

from pyasic.API.cgminer import CGMinerAPI
from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard, MinerData
from pyasic.data.error_codes import MinerErrorData
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner
from pyasic.settings import PyasicSettings


class CGMiner(BaseMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = CGMinerAPI(ip, api_ver)
        self.api_ver = api_ver
        self.api_type = "CGMiner"
        self.uname = "root"
        self.pwd = "admin"
        self.config = None

    async def send_ssh_command(self, cmd: str) -> Optional[str]:
        result = None

        try:
            conn = await self._get_ssh_connection()
        except (asyncssh.Error, OSError):
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

    async def restart_backend(self) -> bool:
        """Restart cgminer hashing process.  Wraps [`restart_cgminer`][pyasic.miners._backends.cgminer.CGMiner.restart_cgminer] to standardize."""
        return await self.restart_cgminer()

    async def restart_cgminer(self) -> bool:
        """Restart cgminer hashing process."""
        commands = ["cgminer-api restart", "/usr/bin/cgminer-monitor >/dev/null 2>&1"]
        commands = ";".join(commands)
        try:
            _ret = await self.send_ssh_command(commands)
        except (asyncssh.Error, OSError):
            return False
        else:
            if isinstance(_ret, str):
                return True
        return False

    async def reboot(self) -> bool:
        """Reboots power to the physical miner."""
        logging.debug(f"{self}: Sending reboot command.")
        try:
            _ret = await self.send_ssh_command("reboot")
        except (asyncssh.Error, OSError):
            return False
        else:
            logging.debug(f"{self}: Reboot command completed.")
            if isinstance(_ret, str):
                return True
        return False

    async def resume_mining(self) -> bool:
        try:
            commands = [
                "mkdir -p /etc/tmp/",
                'echo "*/3 * * * * /usr/bin/cgminer-monitor" > /etc/tmp/root',
                "crontab -u root /etc/tmp/root",
                "/usr/bin/cgminer-monitor >/dev/null 2>&1",
            ]
            commands = ";".join(commands)
            await self.send_ssh_command(commands)
        except (asyncssh.Error, OSError):
            return False
        else:
            return True

    async def stop_mining(self) -> bool:
        try:
            commands = [
                "mkdir -p /etc/tmp/",
                'echo "" > /etc/tmp/root',
                "crontab -u root /etc/tmp/root",
                "killall cgminer",
            ]
            commands = ";".join(commands)
            await self.send_ssh_command(commands)
        except (asyncssh.Error, OSError):
            return False
        else:
            return True

    async def get_config(self, api_pools: dict = None) -> MinerConfig:
        # get pool data
        try:
            api_pools = await self.api.pools()
        except APIError:
            pass

        if api_pools:
            self.config = MinerConfig().from_api(api_pools["POOLS"])
        return self.config

    async def fault_light_off(self) -> bool:
        return False

    async def fault_light_on(self) -> bool:
        return False

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        return None

    async def set_power_limit(self, wattage: int) -> bool:
        return False

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(self) -> Optional[str]:
        return None

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
        return miner_version(
            api_ver=await self.get_api_ver(api_version=api_version),
            fw_ver=await self.get_fw_ver(api_version=api_version),
        )

    async def get_api_ver(self, api_version: dict = None) -> Optional[str]:
        if self.api_ver:
            return self.api_ver

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

        return self.api_ver

    async def get_fw_ver(self, api_version: dict = None) -> Optional[str]:
        if self.fw_ver:
            return self.fw_ver

        if not api_version:
            try:
                api_version = await self.api.version()
            except APIError:
                pass

        if api_version:
            try:
                self.fw_ver = api_version["VERSION"][0]["CGMiner"]
            except (KeyError, IndexError):
                pass

        return self.fw_ver

    async def get_hostname(self) -> Optional[str]:
        try:
            hn = await self.send_ssh_command("cat /proc/sys/kernel/hostname")
        except (asyncssh.Error, OSError):
            return None
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
                return round(
                    float(float(api_summary["SUMMARY"][0]["GHS 5s"]) / 1000), 2
                )
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
                            fan_offset = fan_num
                if fan_offset == -1:
                    fan_offset = 1

                for fan in range(self.fan_count):
                    fans_data[fan] = Fan(
                        api_stats["STATS"][1].get(f"fan{fan_offset+fan}")
                    )
            except (KeyError, IndexError):
                pass
        return fans_data

    async def get_fan_psu(self) -> Optional[int]:
        return None

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
                    rate_unit = "GH"
                if rate_unit == "GH":
                    return round(ideal_rate / 1000, 2)
                if rate_unit == "MH":
                    return round(ideal_rate / 1000000, 2)
                else:
                    return round(ideal_rate, 2)
            except (KeyError, IndexError):
                pass
