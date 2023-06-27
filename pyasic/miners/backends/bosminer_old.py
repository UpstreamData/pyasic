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

import logging
from typing import List, Optional, Tuple

from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard, MinerData
from pyasic.data.error_codes import MinerErrorData
from pyasic.miners.backends import BOSMiner


class BOSMinerOld(BOSMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver)

    async def send_ssh_command(self, cmd: str) -> Optional[str]:
        result = None

        try:
            conn = await self._get_ssh_connection()
        except ConnectionError:
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

    async def get_mac(self, *args, **kwargs) -> Optional[str]:
        return None

    async def get_model(self, *args, **kwargs) -> str:
        return "S9"

    async def get_version(self, *args, **kwargs) -> Tuple[Optional[str], Optional[str]]:
        return None, None

    async def get_hostname(self, *args, **kwargs) -> Optional[str]:
        return None

    async def get_hashrate(self, *args, **kwargs) -> Optional[float]:
        return None

    async def get_hashboards(self, *args, **kwargs) -> List[HashBoard]:
        return []

    async def get_env_temp(self, *args, **kwargs) -> Optional[float]:
        return None

    async def get_wattage(self, *args, **kwargs) -> Optional[int]:
        return None

    async def get_wattage_limit(self, *args, **kwargs) -> Optional[int]:
        return None

    async def get_fans(
        self,
        *args,
        **kwargs,
    ) -> List[Fan]:
        return [Fan(), Fan(), Fan(), Fan()]

    async def get_fan_psu(self, *args, **kwargs) -> Optional[int]:
        return None

    async def get_api_ver(self, *args, **kwargs) -> Optional[str]:
        return None

    async def get_fw_ver(self, *args, **kwargs) -> Optional[str]:
        return None

    async def get_pools(self, *args, **kwargs) -> List[dict]:
        return []

    async def get_errors(self, *args, **kwargs) -> List[MinerErrorData]:
        return []

    async def get_fault_light(self, *args, **kwargs) -> bool:
        return False

    async def get_nominal_hashrate(self, *args, **kwargs) -> Optional[float]:
        return None

    async def get_data(self, allow_warning: bool = False, **kwargs) -> MinerData:
        return MinerData(ip=str(self.ip))

    async def is_mining(self, *args, **kwargs) -> Optional[bool]:
        return None

    async def get_uptime(self, *args, **kwargs) -> Optional[int]:
        return None
