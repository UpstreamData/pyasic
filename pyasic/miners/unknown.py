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

from pyasic.API.unknown import UnknownAPI
from pyasic.miners import BaseMiner


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
