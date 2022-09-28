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
from pyasic.miners._types import (
    M31SPlus,
    M31SPlusVE20,
    M31SPlusV30,
    M31SPlusV40,
    M31SPlusV60,
    M31SPlusV80,
    M31SPlusV90,
)  # noqa - Ignore access to _module


class BTMinerM31SPlus(BTMiner, M31SPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM31SPlusVE20(BTMiner, M31SPlusVE20):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM31SPlusV30(BTMiner, M31SPlusV30):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM31SPlusV40(BTMiner, M31SPlusV40):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM31SPlusV60(BTMiner, M31SPlusV60):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM31SPlusV80(BTMiner, M31SPlusV80):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM31SPlusV90(BTMiner, M31SPlusV90):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
