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

import ipaddress
from typing import Union

from pyasic.miners.base import AnyMiner, BaseMiner
from pyasic.miners.miner_factory import MinerFactory


# abstracted version of get miner that is easier to access
async def get_miner(ip: Union[ipaddress.ip_address, str]) -> AnyMiner:
    return await MinerFactory().get_miner(ip)
