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
from __future__ import annotations

import random
import string
from typing import List

from pydantic import Field

from pyasic.config.base import MinerConfigValue
from pyasic.web.braiins_os.proto.braiins.bos.v1 import (
    PoolConfiguration,
    PoolGroupConfiguration,
    Quota,
    SaveAction,
    SetPoolGroupsRequest,
)


class Pool(MinerConfigValue):
    url: str
    user: str
    password: str

    def as_am_modern(self, user_suffix: str | None = None) -> dict:
        return {
            "url": self.url,
            "user": f"{self.user}{user_suffix or ''}",
            "pass": self.password,
        }

    def as_hiveon_modern(self, user_suffix: str | None = None) -> dict:
        return {
            "url": self.url,
            "user": f"{self.user}{user_suffix or ''}",
            "pass": self.password,
        }

    def as_elphapex(self, user_suffix: str | None = None) -> dict:
        return {
            "url": self.url,
            "user": f"{self.user}{user_suffix or ''}",
            "pass": self.password,
        }

    def as_wm(self, idx: int = 1, user_suffix: str | None = None) -> dict:
        return {
            f"pool_{idx}": self.url,
            f"worker_{idx}": f"{self.user}{user_suffix or ''}",
            f"passwd_{idx}": self.password,
        }

    def as_am_old(self, idx: int = 1, user_suffix: str | None = None) -> dict:
        return {
            f"_ant_pool{idx}url": self.url,
            f"_ant_pool{idx}user": f"{self.user}{user_suffix or ''}",
            f"_ant_pool{idx}pw": self.password,
        }

    def as_goldshell(self, user_suffix: str | None = None) -> dict:
        return {
            "url": self.url,
            "user": f"{self.user}{user_suffix or ''}",
            "pass": self.password,
        }

    def as_avalon(self, user_suffix: str | None = None) -> str:
        return ",".join([self.url, f"{self.user}{user_suffix or ''}", self.password])

    def as_inno(self, idx: int = 1, user_suffix: str | None = None) -> dict:
        return {
            f"Pool{idx}": self.url,
            f"UserName{idx}": f"{self.user}{user_suffix or ''}",
            f"Password{idx}": self.password,
        }

    def as_bosminer(self, user_suffix: str | None = None) -> dict:
        return {
            "url": self.url,
            "user": f"{self.user}{user_suffix or ''}",
            "password": self.password,
        }

    def as_auradine(self, user_suffix: str | None = None) -> dict:
        return {
            "url": self.url,
            "user": f"{self.user}{user_suffix or ''}",
            "pass": self.password,
        }

    def as_epic(self, user_suffix: str | None = None):
        return {
            "pool": self.url,
            "login": f"{self.user}{user_suffix or ''}",
            "password": self.password,
        }

    def as_mara(self, user_suffix: str | None = None) -> dict:
        return {
            "url": self.url,
            "user": f"{self.user}{user_suffix or ''}",
            "pass": self.password,
        }

    def as_espminer(self, user_suffix: str | None = None) -> dict:
        return {
            "stratumURL": self.url,
            "stratumUser": f"{self.user}{user_suffix or ''}",
            "stratumPassword": self.password,
        }

    def as_boser(self, user_suffix: str | None = None) -> PoolConfiguration:
        return PoolConfiguration(
            url=self.url,
            user=f"{self.user}{user_suffix or ''}",
            password=self.password,
            enabled=True,
        )

    def as_vnish(self, user_suffix: str | None = None) -> dict:
        return {
            "url": self.url,
            "user": f"{self.user}{user_suffix or ''}",
            "pass": self.password,
        }

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "Pool":
        return cls(
            url=dict_conf["url"], user=dict_conf["user"], password=dict_conf["password"]
        )

    @classmethod
    def from_api(cls, api_pool: dict) -> "Pool":
        return cls(url=api_pool["URL"], user=api_pool["User"], password="x")

    @classmethod
    def from_epic(cls, api_pool: dict) -> "Pool":
        return cls(
            url=api_pool["pool"], user=api_pool["login"], password=api_pool["password"]
        )

    @classmethod
    def from_am_modern(cls, web_pool: dict) -> "Pool":
        return cls(
            url=web_pool["url"], user=web_pool["user"], password=web_pool["pass"]
        )

    @classmethod
    def from_hiveon_modern(cls, web_pool: dict) -> "Pool":
        return cls(
            url=web_pool["url"], user=web_pool["user"], password=web_pool["pass"]
        )

    @classmethod
    def from_elphapex(cls, web_pool: dict) -> "Pool":
        return cls(
            url=web_pool["url"], user=web_pool["user"], password=web_pool["pass"]
        )

    # TODO: check if this is accurate, user/username, pass/password
    @classmethod
    def from_goldshell(cls, web_pool: dict) -> "Pool":
        return cls(
            url=web_pool["url"], user=web_pool["user"], password=web_pool["pass"]
        )

    @classmethod
    def from_inno(cls, web_pool: dict) -> "Pool":
        return cls(
            url=web_pool["url"], user=web_pool["user"], password=web_pool["pass"]
        )

    @classmethod
    def from_bosminer(cls, toml_pool_conf: dict) -> "Pool":
        return cls(
            url=toml_pool_conf["url"],
            user=toml_pool_conf["user"],
            password=toml_pool_conf["password"],
        )

    @classmethod
    def from_vnish(cls, web_pool: dict) -> "Pool":
        return cls(
            url="stratum+tcp://" + web_pool["url"],
            user=web_pool["user"],
            password=web_pool["pass"],
        )

    @classmethod
    def from_boser(cls, grpc_pool: dict) -> "Pool":
        return cls(
            url=grpc_pool["url"],
            user=grpc_pool["user"],
            password=grpc_pool["password"],
        )

    @classmethod
    def from_mara(cls, web_pool: dict) -> "Pool":
        return cls(
            url=web_pool["url"],
            user=web_pool["user"],
            password=web_pool["pass"],
        )

    @classmethod
    def from_espminer(cls, web_system_info: dict) -> "Pool":
        url = f"stratum+tcp://{web_system_info['stratumURL']}:{web_system_info['stratumPort']}"
        return cls(
            url=url,
            user=web_system_info["stratumUser"],
            password=web_system_info.get("stratumPassword", ""),
        )

    @classmethod
    def from_luxos(cls, rpc_pools: dict) -> "Pool":
        return cls.from_api(rpc_pools)

    @classmethod
    def from_iceriver(cls, web_pool: dict) -> "Pool":
        return cls(
            url=web_pool["addr"],
            user=web_pool["user"],
            password=web_pool["pass"],
        )


class PoolGroup(MinerConfigValue):
    pools: list[Pool] = Field(default_factory=list)
    quota: int = 1
    name: str | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
            )  # generate random pool group name in case it isn't set

    def as_am_modern(self, user_suffix: str | None = None) -> list:
        pools = []
        idx = 0
        while idx < 3:
            if len(self.pools) > idx:
                pools.append(self.pools[idx].as_am_modern(user_suffix=user_suffix))
            else:
                pools.append(Pool(url="", user="", password="").as_am_modern())
            idx += 1
        return pools

    def as_hiveon_modern(self, user_suffix: str | None = None) -> list:
        pools = []
        idx = 0
        while idx < 3:
            if len(self.pools) > idx:
                pools.append(self.pools[idx].as_hiveon_modern(user_suffix=user_suffix))
            else:
                pools.append(Pool(url="", user="", password="").as_hiveon_modern())
            idx += 1
        return pools

    def as_elphapex(self, user_suffix: str | None = None) -> list:
        pools = []
        idx = 0
        while idx < 3:
            if len(self.pools) > idx:
                pools.append(self.pools[idx].as_elphapex(user_suffix=user_suffix))
            else:
                pools.append(Pool(url="", user="", password="").as_elphapex())
            idx += 1
        return pools

    def as_wm(self, user_suffix: str | None = None) -> dict:
        pools = {}
        idx = 0
        while idx < 3:
            if len(self.pools) > idx:
                pools.update(
                    **self.pools[idx].as_wm(idx=idx + 1, user_suffix=user_suffix)
                )
            else:
                pools.update(**Pool(url="", user="", password="").as_wm(idx=idx + 1))
            idx += 1
        return pools

    def as_am_old(self, user_suffix: str | None = None) -> dict:
        pools = {}
        idx = 0
        while idx < 3:
            if len(self.pools) > idx:
                pools.update(
                    **self.pools[idx].as_am_old(idx=idx + 1, user_suffix=user_suffix)
                )
            else:
                pools.update(
                    **Pool(url="", user="", password="").as_am_old(idx=idx + 1)
                )
            idx += 1
        return pools

    def as_goldshell(self, user_suffix: str | None = None) -> list:
        return [pool.as_goldshell(user_suffix) for pool in self.pools]

    def as_avalon(self, user_suffix: str | None = None) -> str:
        if len(self.pools) > 0:
            return self.pools[0].as_avalon(user_suffix=user_suffix)
        return Pool(url="", user="", password="").as_avalon()

    def as_inno(self, user_suffix: str | None = None) -> dict:
        pools = {}
        idx = 0
        while idx < 3:
            if len(self.pools) > idx:
                pools.update(
                    **self.pools[idx].as_inno(idx=idx + 1, user_suffix=user_suffix)
                )
            else:
                pools.update(**Pool(url="", user="", password="").as_inno(idx=idx + 1))
            idx += 1
        return pools

    def as_bosminer(self, user_suffix: str | None = None) -> dict:
        if len(self.pools) > 0:
            conf = {
                "name": self.name,
                "pool": [
                    pool.as_bosminer(user_suffix=user_suffix) for pool in self.pools
                ],
            }
            if self.quota is not None:
                conf["quota"] = self.quota
            return conf
        return {"name": "Group", "pool": []}

    def as_auradine(self, user_suffix: str | None = None) -> list:
        return [p.as_auradine(user_suffix=user_suffix) for p in self.pools]

    def as_epic(self, user_suffix: str | None = None) -> list:
        return [p.as_epic(user_suffix=user_suffix) for p in self.pools]

    def as_mara(self, user_suffix: str | None = None) -> list:
        return [p.as_mara(user_suffix=user_suffix) for p in self.pools]

    def as_espminer(self, user_suffix: str | None = None) -> dict:
        return self.pools[0].as_espminer(user_suffix=user_suffix)

    def as_boser(self, user_suffix: str | None = None) -> PoolGroupConfiguration:
        return PoolGroupConfiguration(
            name=self.name,
            quota=Quota(value=self.quota),
            pools=[p.as_boser() for p in self.pools],
        )

    def as_vnish(self, user_suffix: str | None = None) -> dict:
        return {"pools": [p.as_vnish(user_suffix=user_suffix) for p in self.pools]}

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "PoolGroup":
        cls_conf = {}

        if dict_conf.get("quota") is not None:
            cls_conf["quota"] = dict_conf["quota"]
        if dict_conf.get("name") is not None:
            cls_conf["name"] = dict_conf["name"]
        cls_conf["pools"] = [Pool.from_dict(p) for p in dict_conf["pools"]]
        return cls(**cls_conf)

    @classmethod
    def from_api(cls, api_pool_list: list) -> "PoolGroup":
        pools = []
        for pool in api_pool_list:
            pools.append(Pool.from_api(pool))
        return cls(pools=pools)

    @classmethod
    def from_epic(cls, api_pool_list: list) -> "PoolGroup":
        pools = []
        for pool in api_pool_list:
            pools.append(Pool.from_epic(pool))
        return cls(pools=pools)

    @classmethod
    def from_am_modern(cls, web_pool_list: list) -> "PoolGroup":
        pools = []
        for pool in web_pool_list:
            pools.append(Pool.from_am_modern(pool))
        return cls(pools=pools)

    @classmethod
    def from_hiveon_modern(cls, web_pool_list: list) -> "PoolGroup":
        pools = []
        for pool in web_pool_list:
            pools.append(Pool.from_hiveon_modern(pool))
        return cls(pools=pools)

    @classmethod
    def from_elphapex(cls, web_pool_list: list) -> "PoolGroup":
        pools = []
        for pool in web_pool_list:
            pools.append(Pool.from_elphapex(pool))
        return cls(pools=pools)

    @classmethod
    def from_goldshell(cls, web_pools: list) -> "PoolGroup":
        return cls(pools=[Pool.from_goldshell(p) for p in web_pools])

    @classmethod
    def from_inno(cls, web_pools: list) -> "PoolGroup":
        return cls(pools=[Pool.from_inno(p) for p in web_pools])

    @classmethod
    def from_bosminer(cls, toml_group_conf: dict) -> "PoolGroup":
        if toml_group_conf.get("pool") is not None:
            return cls(
                name=toml_group_conf["name"],
                quota=toml_group_conf.get("quota", 1),
                pools=[Pool.from_bosminer(p) for p in toml_group_conf["pool"]],
            )
        return cls()

    @classmethod
    def from_vnish(cls, web_settings_pools: dict) -> "PoolGroup":
        return cls(
            pools=[Pool.from_vnish(p) for p in web_settings_pools if p["url"] != ""]
        )

    @classmethod
    def from_boser(cls, grpc_pool_group: dict) -> "PoolGroup":
        try:
            return cls(
                pools=[Pool.from_boser(p) for p in grpc_pool_group["pools"]],
                name=grpc_pool_group["name"],
                quota=(
                    grpc_pool_group["quota"]["value"]
                    if grpc_pool_group.get("quota") is not None
                    else 1
                ),
            )
        except LookupError:
            return cls()

    @classmethod
    def from_mara(cls, web_config_pools: dict) -> "PoolGroup":
        return cls(pools=[Pool.from_mara(pool_conf) for pool_conf in web_config_pools])

    @classmethod
    def from_espminer(cls, web_system_info: dict) -> "PoolGroup":
        return cls(pools=[Pool.from_espminer(web_system_info)])

    @classmethod
    def from_iceriver(cls, web_userpanel: dict) -> "PoolGroup":
        return cls(
            pools=[
                Pool.from_iceriver(web_pool)
                for web_pool in web_userpanel["data"]["pools"]
            ]
        )


class PoolConfig(MinerConfigValue):
    groups: List[PoolGroup] = Field(default_factory=list)

    @classmethod
    def default(cls) -> "PoolConfig":
        return cls()

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "PoolConfig":
        if dict_conf is None:
            return cls.default()

        return cls(groups=[PoolGroup.from_dict(g) for g in dict_conf["groups"]])

    @classmethod
    def simple(cls, pools: list[Pool | dict[str, str]]) -> "PoolConfig":
        group_pools = []
        for pool in pools:
            if isinstance(pool, dict):
                pool = Pool(**pool)
            group_pools.append(pool)
        return cls(groups=[PoolGroup(pools=group_pools)])

    def as_am_modern(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return {"pools": self.groups[0].as_am_modern(user_suffix=user_suffix)}
        return {"pools": PoolGroup().as_am_modern()}

    def as_hiveon_modern(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return {"pools": self.groups[0].as_hiveon_modern(user_suffix=user_suffix)}
        return {"pools": PoolGroup().as_hiveon_modern()}

    def as_elphapex(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return {"pools": self.groups[0].as_elphapex(user_suffix=user_suffix)}
        return {"pools": PoolGroup().as_elphapex()}

    def as_wm(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return {"pools": self.groups[0].as_wm(user_suffix=user_suffix)}
        return {"pools": PoolGroup().as_wm()}

    def as_am_old(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return self.groups[0].as_am_old(user_suffix=user_suffix)
        return PoolGroup().as_am_old()

    def as_goldshell(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return {"pools": self.groups[0].as_goldshell(user_suffix=user_suffix)}
        return {"pools": PoolGroup().as_goldshell()}

    def as_avalon(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return {"pools": self.groups[0].as_avalon(user_suffix=user_suffix)}
        return {"pools": PoolGroup().as_avalon()}

    def as_inno(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return self.groups[0].as_inno(user_suffix=user_suffix)
        return PoolGroup().as_inno()

    def as_bosminer(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return {
                "group": [g.as_bosminer(user_suffix=user_suffix) for g in self.groups]
            }
        return {"group": [PoolGroup().as_bosminer()]}

    def as_boser(self, user_suffix: str | None = None) -> dict:
        return {
            "set_pool_groups": SetPoolGroupsRequest(
                save_action=SaveAction.SAVE_AND_APPLY,
                pool_groups=[g.as_boser(user_suffix=user_suffix) for g in self.groups],
            )
        }

    def as_auradine(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return {
                "updatepools": {
                    "pools": self.groups[0].as_auradine(user_suffix=user_suffix)
                }
            }
        return {"updatepools": {"pools": PoolGroup().as_auradine()}}

    def as_epic(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return {
                "pools": {
                    "coin": "Btc",
                    "stratum_configs": self.groups[0].as_epic(user_suffix=user_suffix),
                    "unique_id": False,
                }
            }
        return {
            "pools": {
                "coin": "Btc",
                "stratum_configs": [PoolGroup().as_epic()],
                "unique_id": False,
            }
        }

    def as_mara(self, user_suffix: str | None = None) -> dict:
        if len(self.groups) > 0:
            return {"pools": self.groups[0].as_mara(user_suffix=user_suffix)}
        return {"pools": []}

    def as_espminer(self, user_suffix: str | None = None) -> dict:
        return self.groups[0].as_espminer(user_suffix=user_suffix)

    def as_luxos(self, user_suffix: str | None = None) -> dict:
        return {}

    def as_vnish(self, user_suffix: str | None = None) -> dict:
        return self.groups[0].as_vnish(user_suffix=user_suffix)

    @classmethod
    def from_api(cls, api_pools: dict) -> "PoolConfig":
        try:
            pool_data = api_pools["POOLS"]
        except KeyError:
            return PoolConfig.default()
        pool_data = sorted(pool_data, key=lambda x: int(x["POOL"]))

        return cls(groups=[PoolGroup.from_api(pool_data)])

    @classmethod
    def from_epic(cls, web_conf: dict) -> "PoolConfig":
        pool_data = web_conf["StratumConfigs"]
        return cls(groups=[PoolGroup.from_epic(pool_data)])

    @classmethod
    def from_am_modern(cls, web_conf: dict) -> "PoolConfig":
        try:
            pool_data = web_conf["pools"]
        except KeyError:
            return cls(groups=[])

        return cls(groups=[PoolGroup.from_am_modern(pool_data)])

    @classmethod
    def from_hiveon_modern(cls, web_conf: dict) -> "PoolConfig":
        try:
            pool_data = web_conf["pools"]
        except KeyError:
            return cls(groups=[])

        return cls(groups=[PoolGroup.from_hiveon_modern(pool_data)])

    @classmethod
    def from_elphapex(cls, web_conf: dict) -> "PoolConfig":
        pool_data = web_conf["pools"]

        return cls(groups=[PoolGroup.from_elphapex(pool_data)])

    @classmethod
    def from_goldshell(cls, web_pools: list) -> "PoolConfig":
        return cls(groups=[PoolGroup.from_goldshell(web_pools)])

    @classmethod
    def from_inno(cls, web_pools: list) -> "PoolConfig":
        return cls(groups=[PoolGroup.from_inno(web_pools)])

    @classmethod
    def from_bosminer(cls, toml_conf: dict) -> "PoolConfig":
        if toml_conf.get("group") is None:
            return cls()

        return cls(groups=[PoolGroup.from_bosminer(g) for g in toml_conf["group"]])

    @classmethod
    def from_vnish(cls, web_settings: dict) -> "PoolConfig":
        try:
            return cls(groups=[PoolGroup.from_vnish(web_settings["miner"]["pools"])])
        except LookupError:
            return cls()

    @classmethod
    def from_boser(cls, grpc_miner_conf: dict) -> "PoolConfig":
        try:
            return cls(
                groups=[
                    PoolGroup.from_boser(group)
                    for group in grpc_miner_conf["poolGroups"]
                ]
            )
        except LookupError:
            return cls()

    @classmethod
    def from_mara(cls, web_config: dict) -> "PoolConfig":
        return cls(groups=[PoolGroup.from_mara(web_config["pools"])])

    @classmethod
    def from_espminer(cls, web_system_info: dict) -> "PoolConfig":
        return cls(groups=[PoolGroup.from_espminer(web_system_info)])

    @classmethod
    def from_iceriver(cls, web_userpanel: dict) -> "PoolConfig":
        return cls(groups=[PoolGroup.from_iceriver(web_userpanel)])

    @classmethod
    def from_luxos(cls, rpc_groups: dict, rpc_pools: dict) -> "PoolConfig":
        return cls(
            groups=[
                PoolGroup(
                    pools=[
                        Pool.from_luxos(pool)
                        for pool in rpc_pools["POOLS"]
                        if pool["GROUP"] == group["GROUP"]
                    ],
                    name=group["Name"],
                    quota=group["Quota"],
                )
                for group in rpc_groups["GROUPS"]
            ]
        )
