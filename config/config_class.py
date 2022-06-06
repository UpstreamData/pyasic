from dataclasses import dataclass, asdict
from typing import List, Literal
import random
import string


@dataclass
class _Pool:
    url: str = ""
    username: str = ""
    password: str = ""

    def from_dict(self, data: dict):
        for key in data.keys():
            if key == "url":
                self.url = data[key]
            if key in ["user", "username"]:
                self.username = data[key]
            if key in ["pass", "password"]:
                self.password = data[key]
        return self


@dataclass
class _PoolGroup:
    pools: List[_Pool] = None
    quota: int = 1
    group_name: str = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )  # generate random pool group name in case it isn't set

    def from_dict(self, data: dict):
        pools = []
        for key in data.keys():
            if key == "name":
                self.group_name = data[key]
            if key == "quota":
                self.quota = data[key]
            if key in ["pools", "pool"]:
                for pool in data[key]:
                    pools.append(_Pool().from_dict(pool))
        self.pools = pools
        return self


@dataclass
class MinerConfig:
    pool_groups: List[_PoolGroup] = None

    temp_mode: Literal["auto", "manual", "disabled"] = "auto"
    temp_target: float = 70.0
    temp_hot: float = 80.0
    temp_dangerous: float = 10.0

    minimum_fans: int = None
    fan_speed: Literal[tuple(range(101))] = None  # noqa - Ignore weird Literal usage

    asicboost: bool = None

    autotuning_enabled: bool = True
    autotuning_wattage: int = 900

    dps_enabled: bool = None
    dps_power_step: int = None
    dps_min_power: int = None
    dps_shutdown_enabled: bool = None
    dps_shutdown_duration: float = None

    def as_dict(self):
        data_dict = asdict(self)
        for key in asdict(self).keys():
            if data_dict[key] == None:
                del data_dict[key]
        return data_dict

    def from_dict(self, data: dict):
        pool_groups = []
        for key in data.keys():
            if key == "pools":
                pool_groups.append(_PoolGroup().from_dict({"pools": data[key]}))
            elif key == "group":
                for group in data[key]:
                    pool_groups.append(_PoolGroup().from_dict(group))

            if key == "bitmain-fan-ctrl":
                if data[key]:
                    self.temp_mode = "manual"
            elif key == "bitmain-fan-pwm":
                self.fan_speed = data[key]
            elif key == "fan_control":
                for _key in data[key].keys():
                    if _key == "min_fans":
                        self.minimum_fans = data[key][_key]
                    elif _key == "speed":
                        self.fan_speed = data[key][_key]
            elif key == "temp_control":
                for _key in data[key].keys():
                    if _key == "mode":
                        self.temp_mode = data[key][_key]
                    elif _key == "target_temp":
                        self.temp_target = data[key][_key]
                    elif _key == "hot_temp":
                        self.temp_hot = data[key][_key]
                    elif _key == "dangerous_temp":
                        self.temp_dangerous = data[key][_key]

            if key == "hash_chain_global":
                if data[key].get("asic_boost"):
                    self.asicboost = data[key]["asic_boost"]

            if key == "autotuning":
                for _key in data[key].keys():
                    if _key == "enabled":
                        self.autotuning_enabled = data[key][_key]
                    elif _key == "psu_power_limit":
                        self.autotuning_wattage = data[key][_key]

            if key == "power_scaling":
                for _key in data[key].keys():
                    if _key == "enabled":
                        self.dps_enabled = data[key][_key]
                    elif _key == "power_step":
                        self.dps_power_step = data[key][_key]
                    elif _key == "min_psu_power_limit":
                        self.dps_min_power = data[key][_key]
                    elif _key == "shutdown_enabled":
                        self.dps_shutdown_enabled = data[key][_key]
                    elif _key == "shutdown_duration":
                        self.dps_shutdown_duration = data[key][_key]

        self.pool_groups = pool_groups
        return self


if __name__ == "__main__":
    import pprint
    import json

    bos_conf = {
        "group": [
            {
                "name": "group",
                "pool": [
                    {
                        "password": "123",
                        "url": "stratum2+tcp://v2.us-east.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt",
                        "user": "UpstreamDataInc.test",
                    },
                    {
                        "password": "123",
                        "url": "stratum2+tcp://v2.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt",
                        "user": "UpstreamDataInc.test",
                    },
                    {
                        "password": "123",
                        "url": "stratum+tcp://stratum.slushpool.com:3333",
                        "user": "UpstreamDataInc.test",
                    },
                ],
                "quota": 1,
            },
            {
                "name": "group_2",
                "pool": [
                    {
                        "password": "123",
                        "url": "stratum2+tcp://v2.us-east.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt",
                        "user": "UpstreamDataInc.test",
                    },
                    {
                        "password": "123",
                        "url": "stratum2+tcp://v2.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt",
                        "user": "UpstreamDataInc.test",
                    },
                    {
                        "password": "123",
                        "url": "stratum+tcp://stratum.slushpool.com:3333",
                        "user": "UpstreamDataInc.test",
                    },
                ],
                "quota": 1,
            },
        ],
    }

    pprint.pprint(MinerConfig().from_dict(bos_conf).as_dict())
