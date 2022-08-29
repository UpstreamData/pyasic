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

from pyasic.miners._backends import BTMiner  # noqa - Ignore access to _module
from pyasic.miners._types import (  # noqa - Ignore access to _module
    M30SPlusPlus,
    M30SPlusPlusVG40,
    M30SPlusPlusVG30,
    M30SPlusPlusVH60,
)


class BTMinerM30SPlusPlus(BTMiner, M30SPlusPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM30SPlusPlusVG30(BTMiner, M30SPlusPlusVG30):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM30SPlusPlusVG40(BTMiner, M30SPlusPlusVG40):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM30SPlusPlusVH60(BTMiner, M30SPlusPlusVH60):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
