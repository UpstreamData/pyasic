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

from typing import List

from pyasic.API.unknown import UnknownAPI
from pyasic.config import MinerConfig
from pyasic.data import MinerData
from pyasic.data.error_codes import MinerErrorData
from pyasic.miners.base import BaseMiner


class UnknownMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        super().__init__()
        self.ip = ip
        self.api = UnknownAPI(ip)
        self.model = "Unknown"

    def __repr__(self) -> str:
        return f"Unknown: {str(self.ip)}"

    async def get_model(self):
        return "Unknown"

    async def get_hostname(self):
        return "Unknown"

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

    async def get_errors(self) -> List[MinerErrorData]:
        return []

    async def get_mac(self) -> str:
        return "00:00:00:00:00:00"

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

    async def get_data(self, allow_warning: bool = False) -> MinerData:
        return MinerData(ip=str(self.ip))

    async def set_power_limit(self, wattage: int) -> bool:
        return False
