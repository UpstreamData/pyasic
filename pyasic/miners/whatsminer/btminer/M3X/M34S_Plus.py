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
    M34SPlus,
    M34SPlusVE10,
)


class BTMinerM34SPlus(BTMiner, M34SPlus):
    def __init__(self, ip: str, api_ver: str = "1.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        self.ip = ip


class BTMinerM34SPlusVE10(BTMiner, M34SPlusVE10):
    def __init__(self, ip: str, api_ver: str = "1.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        self.ip = ip
