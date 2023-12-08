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
import random
import string
from dataclasses import dataclass, field
from typing import Union


@dataclass
class Pool:
    url: str
    user: str
    password: str


@dataclass
class PoolGroup:
    pools: list[Pool] = field(default_factory=list)
    quota: int = 1
    name: str = None

    def __post_init__(self):
        if self.group_name is None:
            self.group_name = "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
            )  # generate random pool group name in case it isn't set


@dataclass
class PoolConfig:
    groups: list[PoolGroup] = field(default_factory=list)

    @classmethod
    def default(cls):
        return cls()

    def simple(self, pools: list[Union[Pool, dict[str, str]]]):
        group_pools = []
        for pool in pools:
            if isinstance(pool, dict):
                pool = Pool(**pool)
            group_pools.append(pool)
        self.groups = [PoolGroup(pools=group_pools)]
