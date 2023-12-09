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

from pyasic.config.base import MinerConfigValue


@dataclass
class Pool(MinerConfigValue):
    url: str
    user: str
    password: str

    def as_am_modern(self, user_suffix: str = None):
        if user_suffix is not None:
            return {
                "url": self.url,
                "user": f"{self.user}{user_suffix}",
                "pass": self.password,
            }
        return {"url": self.url, "user": self.user, "pass": self.password}

    def as_wm(self, idx: int, user_suffix: str = None):
        if user_suffix is not None:
            return {
                f"pool_{idx}": self.url,
                f"worker_{idx}": f"{self.user}{user_suffix}",
                f"passwd_{idx}": self.password,
            }
        return {
            f"pool_{idx}": self.url,
            f"worker_{idx}": self.user,
            f"passwd_{idx}": self.password,
        }

    def as_am_old(self, idx: int, user_suffix: str = None):
        if user_suffix is not None:
            return {
                f"_ant_pool{idx}url": self.url,
                f"_ant_pool{idx}user": f"{self.user}{user_suffix}",
                f"_ant_pool{idx}pw": self.password,
            }
        return {
            f"_ant_pool{idx}url": self.url,
            f"_ant_pool{idx}user": self.user,
            f"_ant_pool{idx}pw": self.password,
        }

    def as_goldshell(self, user_suffix: str = None):
        if user_suffix is not None:
            return {
                "url": self.url,
                "user": f"{self.user}{user_suffix}",
                "pass": self.password,
            }
        return {"url": self.url, "user": self.user, "pass": self.password}

    def as_avalon(self, user_suffix: str = None):
        if user_suffix is not None:
            return ",".join([self.url, f"{self.user}{user_suffix}", self.password])
        return ",".join([self.url, self.user, self.password])

    def as_inno(self, idx: int, user_suffix: str = None):
        if user_suffix is not None:
            return {
                f"Pool{idx}": self.url,
                f"UserName{idx}": f"{self.user}{user_suffix}",
                f"Password{idx}": self.password,
            }
        return {
            f"Pool{idx}": self.url,
            f"UserName{idx}": self.user,
            f"Password{idx}": self.password,
        }


    def as_bosminer(self, user_suffix: str = None):
        if user_suffix is not None:
            return {
                "url": self.url,
                "user": f"{self.user}{user_suffix}",
                "pass": self.password,
            }
        return {"url": self.url, "user": self.user, "pass": self.password}

    @classmethod
    def from_api(cls, api_pool: dict):
        return cls(url=api_pool["URL"], user=api_pool["User"], password="x")

    @classmethod
    def from_am_modern(cls, web_pool: dict):
        return cls(url=web_pool["url"], user=web_pool["user"], password=web_pool["pass"])


@dataclass
class PoolGroup(MinerConfigValue):
    pools: list[Pool] = field(default_factory=list)
    quota: int = 1
    name: str = None

    def __post_init__(self):
        if self.name is None:
            self.name = "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
            )  # generate random pool group name in case it isn't set

    def as_am_modern(self, user_suffix: str = None) -> list:
        pools = []
        idx = 0
        while idx < 3:
            if len(self.pools) > idx:
                pools.append(self.pools[idx].as_am_modern(user_suffix=user_suffix))
            else:
                pools.append(Pool("", "", "").as_am_modern())
            idx += 1
        return pools

    def as_wm(self, user_suffix: str = None) -> dict:
        pools = {}
        idx = 0
        while idx < 3:
            if len(self.pools) > idx:
                pools.update(
                    **self.pools[idx].as_wm(idx=idx + 1, user_suffix=user_suffix)
                )
            else:
                pools.update(**Pool("", "", "").as_wm(idx=idx + 1))
            idx += 1
        return pools

    def as_am_old(self, user_suffix: str = None) -> dict:
        pools = {}
        idx = 0
        while idx < 3:
            if len(self.pools) > idx:
                pools.update(
                    **self.pools[idx].as_am_old(idx=idx + 1, user_suffix=user_suffix)
                )
            else:
                pools.update(**Pool("", "", "").as_am_old(idx=idx + 1))
            idx += 1
        return pools

    def as_goldshell(self, user_suffix: str = None) -> list:
        pools = []
        idx = 0
        while idx < 3:
            if len(self.pools) > idx:
                pools.append(self.pools[idx].as_am_modern(user_suffix=user_suffix))
            else:
                pools.append(Pool("", "", "").as_am_modern())
            idx += 1
        return pools

    def as_avalon(self, user_suffix: str = None) -> dict:
        if len(self.pools) > 0:
            return self.pools[0].as_avalon(user_suffix=user_suffix)
        return Pool("", "", "").as_avalon()

    def as_inno(self, user_suffix: str = None) -> dict:
        pools = {}
        idx = 0
        while idx < 3:
            if len(self.pools) > idx:
                pools.update(
                    **self.pools[idx].as_inno(idx=idx + 1, user_suffix=user_suffix)
                )
            else:
                pools.update(**Pool("", "", "").as_inno(idx=idx + 1))
            idx += 1
        return pools

    def as_bosminer(self, user_suffix: str = None) -> dict:
        if len(self.pools) > 0:
            return {
                "name": self.name,
                "quota": self.quota,
                "pool": [
                    pool.as_bosminer(user_suffix=user_suffix) for pool in self.pools
                ],
            }
        return {"name": "Group", "quota": 1, "pool": [Pool.as_bosminer()]}

    @classmethod
    def from_api(cls, api_pool_list: list):
        pools = []
        for pool in api_pool_list:
            pools.append(Pool.from_api(pool))
        return cls(pools=pools)

    @classmethod
    def from_am_modern(cls, web_pool_list: list):
        pools = []
        for pool in web_pool_list:
            pools.append(Pool.from_am_modern(pool))
        return cls(pools=pools)



@dataclass
class PoolConfig(MinerConfigValue):
    groups: list[PoolGroup] = field(default_factory=list)

    @classmethod
    def default(cls):
        return cls()

    @classmethod
    def simple(cls, pools: list[Union[Pool, dict[str, str]]]):
        group_pools = []
        for pool in pools:
            if isinstance(pool, dict):
                pool = Pool(**pool)
            group_pools.append(pool)
        return cls(groups=[PoolGroup(pools=group_pools)])

    def as_am_modern(self, user_suffix: str = None) -> dict:
        if len(self.groups) > 0:
            return {"pools": self.groups[0].as_am_modern(user_suffix=user_suffix)}
        return {"pools": PoolGroup().as_am_modern()}

    def as_wm(self, user_suffix: str = None) -> dict:
        if len(self.groups) > 0:
            return {"pools": self.groups[0].as_wm(user_suffix=user_suffix)}
        return {"pools": PoolGroup().as_wm()}

    def as_am_old(self, user_suffix: str = None) -> dict:
        if len(self.groups) > 0:
            return self.groups[0].as_am_old(user_suffix=user_suffix)
        return PoolGroup().as_am_old()

    def as_goldshell(self, user_suffix: str = None) -> dict:
        if len(self.groups) > 0:
            return {"pools": self.groups[0].as_goldshell(user_suffix=user_suffix)}
        return {"pools": PoolGroup().as_goldshell()}

    def as_avalon(self, user_suffix: str = None) -> dict:
        if len(self.groups) > 0:
            return {"pools": self.groups[0].as_avalon(user_suffix=user_suffix)}
        return {"pools": PoolGroup().as_avalon()}

    def as_inno(self, user_suffix: str = None) -> dict:
        if len(self.groups) > 0:
            return self.groups[0].as_inno(user_suffix=user_suffix)
        return PoolGroup().as_inno()


    def as_bosminer(self, user_suffix: str = None) -> dict:
        if len(self.groups) > 0:
            return {
                "group": [g.as_bosminer(user_suffix=user_suffix) for g in self.groups]
            }
        return {"group": [PoolGroup().as_bosminer()]}

    @classmethod
    def from_api(cls, api_pools: dict):
        pool_data = api_pools["POOLS"]
        pool_data = sorted(pool_data, key=lambda x: int(x["POOL"]))

        return cls([PoolGroup.from_api(pool_data)])

    @classmethod
    def from_am_modern(cls, web_conf: dict):
        pool_data = web_conf["pools"]

        return cls([PoolGroup.from_am_modern(pool_data)])
