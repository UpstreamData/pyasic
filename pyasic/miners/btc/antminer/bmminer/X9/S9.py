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

from typing import Union

from pyasic.miners.backends import BMMiner
from pyasic.miners.btc._types import S9  # noqa - Ignore access to _module
from pyasic.web.S9 import S9WebAPI


class BMMinerS9(BMMiner, S9):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        self.ip = ip
        self.web = S9WebAPI(ip)

    async def get_mac(self) -> Union[str, None]:
        try:
            data = await self.web.get_system_info()
            if data:
                return data["macaddr"]
        except KeyError:
            pass

        try:
            data = await self.web.get_network_info()
            if data:
                return data["macaddr"]
        except KeyError:
            pass
