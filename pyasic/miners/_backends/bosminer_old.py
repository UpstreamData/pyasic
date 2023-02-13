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

from pyasic.API.bosminer import BOSMinerAPI
from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard, MinerData
from pyasic.data.error_codes import MinerErrorData
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner


class BOSMinerOld(BaseMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = BOSMinerAPI(ip, api_ver)
        self.api_type = "BOSMiner"
        self.uname = "root"
        self.pwd = "admin"

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

    async def update_to_plus(self):
        result = await self.send_ssh_command("opkg update && opkg install bos_plus")
        return result

    async def check_light(self) -> bool:
        return False

    async def fault_light_on(self) -> bool:
        return False

    async def fault_light_off(self) -> bool:
        return False

    async def get_config(self) -> None:
        return None

    async def reboot(self) -> bool:
        return False

    async def restart_backend(self) -> bool:
        return False

    async def stop_mining(self) -> bool:
        return False

    async def resume_mining(self) -> bool:
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

    async def get_model(self) -> str:
        return "S9"

    async def get_version(self) -> Tuple[Optional[str], Optional[str]]:
        return None, None

    async def get_hostname(self) -> Optional[str]:
        return None

    async def get_hashrate(self) -> Optional[float]:
        return None

    async def get_hashboards(self) -> List[HashBoard]:
        return []

    async def get_env_temp(self) -> Optional[float]:
        return None

    async def get_wattage(self) -> Optional[int]:
        return None

    async def get_wattage_limit(self) -> Optional[int]:
        return None

    async def get_fans(
        self,
    ) -> List[Fan]:
        return [Fan(), Fan(), Fan(), Fan()]

    async def get_fan_psu(self) -> Optional[int]:
        return None

    async def get_api_ver(self) -> Optional[str]:
        return None

    async def get_fw_ver(self) -> Optional[str]:
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

    async def get_nominal_hashrate(self) -> Optional[float]:
        return None

    async def get_data(self, allow_warning: bool = False) -> MinerData:
        return MinerData(ip=str(self.ip))
