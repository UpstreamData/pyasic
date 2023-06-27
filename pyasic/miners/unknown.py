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

from typing import List, Optional, Tuple

from pyasic.API.unknown import UnknownAPI
from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard, MinerData
from pyasic.data.error_codes import MinerErrorData
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner


class UnknownMiner(BaseMiner):
    def __init__(
        self,
        ip: str,
        *args,
        **kwargs,  # noqa - ignore *args and **kwargs for signature consistency
    ) -> None:
        super().__init__(ip)
        self.ip = ip
        self.api = UnknownAPI(ip)
        self.model = "Unknown"

    def __repr__(self) -> str:
        return f"Unknown: {str(self.ip)}"

    async def check_light(self) -> bool:
        if not self.light:
            self.light = False
        return self.light

    async def fault_light_off(self) -> bool:
        return False

    async def fault_light_on(self) -> bool:
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

    async def is_mining(self, *args, **kwargs) -> Optional[bool]:
        return None

    async def get_uptime(self, *args, **kwargs) -> Optional[int]:
        return None

    async def get_data(
        self, allow_warning: bool = False, data_to_get: list = None
    ) -> MinerData:
        return MinerData(ip=str(self.ip))
