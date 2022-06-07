from dataclasses import dataclass, asdict
from typing import List, Literal
import random
import string

import toml
import yaml
import json
import time


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

    def as_x19(self, user_suffix: str = None):
        username = self.username
        if user_suffix:
            username = f"{username}{user_suffix}"

        pool = {"url": self.url, "user": username, "pass": self.password}
        return pool

    def as_bos(self, user_suffix: str = None):
        username = self.username
        if user_suffix:
            username = f"{username}{user_suffix}"

        pool = {"url": self.url, "user": username, "password": self.password}
        return pool


@dataclass
class _PoolGroup:
    quota: int = 1
    group_name: str = None
    pools: List[_Pool] = None

    def __post_init__(self):
        if not self.group_name:
            self.group_name = "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
            )  # generate random pool group name in case it isn't set

    def from_dict(self, data: dict):
        pools = []
        for key in data.keys():
            if key in ["name", "group_name"]:
                self.group_name = data[key]
            if key == "quota":
                self.quota = data[key]
            if key in ["pools", "pool"]:
                for pool in data[key]:
                    pools.append(_Pool().from_dict(pool))
        self.pools = pools
        return self

    def as_x19(self, user_suffix: str = None):
        pools = []
        for pool in self.pools[:3]:
            pools.append(pool.as_x19(user_suffix=user_suffix))
        return pools

    def as_bos(self, user_suffix: str = None):
        group = {
            "name": self.group_name,
            "quota": self.quota,
            "pool": [pool.as_bos(user_suffix=user_suffix) for pool in self.pools],
        }
        return group


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
            if data_dict[key] is None:
                del data_dict[key]
        return data_dict

    def as_toml(self):
        return toml.dumps(self.as_dict())

    def as_yaml(self):
        return yaml.dump(self.as_dict(), sort_keys=False)

    def from_raw(self, data: dict):
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
                    if data.get("bitmain-fan-pwm"):
                        self.fan_speed = int(data["bitmain-fan-pwm"])
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

    def from_dict(self, data: dict):
        pool_groups = []
        for group in data["pool_groups"]:
            pool_groups.append(_PoolGroup().from_dict(group))
        for key in data.keys():
            if getattr(self, key) and not key == "pool_groups":
                setattr(self, key, data[key])
        self.pool_groups = pool_groups
        return self

    def from_toml(self, data: str):
        return self.from_dict(toml.loads(data))

    def from_yaml(self, data: str):
        return self.from_dict(yaml.load(data, Loader=yaml.SafeLoader))

    def as_x19(self, user_suffix: str = None):
        cfg = {
            "pools": self.pool_groups[0].as_x19(user_suffix=user_suffix),
            "bitmain-fan-ctrl": False,
            "bitmain-fan-pwn": 100,
        }

        if not self.temp_mode == "auto":
            cfg["bitmain-fan-ctrl"] = True

        if self.fan_speed:
            cfg["bitmain-fan-ctrl"] = str(self.fan_speed)

        return json.dumps(cfg)

    def as_bos(self, model: str = "S9", user_suffix: str = None):
        cfg = {
            "format": {
                "version": "1.2+",
                "model": f"Antminer {model}",
                "generator": "Upstream Config Utility",
                "timestamp": int(time.time()),
            },
            "group": [
                group.as_bos(user_suffix=user_suffix) for group in self.pool_groups
            ],
            "temp_control": {
                "mode": self.temp_mode,
                "target_temp": self.temp_target,
                "hot_temp": self.temp_hot,
                "dangerous_temp": self.temp_dangerous,
            },
        }

        if self.autotuning_enabled or self.autotuning_wattage:
            cfg["autotuning"] = {}
            if self.autotuning_enabled:
                cfg["autotuning"]["enabled"] = self.autotuning_enabled
            if self.autotuning_wattage:
                cfg["autotuning"]["psu_power_limit"] = self.autotuning_wattage

        if self.asicboost:
            cfg["hash_chain_global"] = {}
            cfg["hash_chain_global"]["asic_boost"] = self.asicboost

        if any(
            [
                getattr(self, item)
                for item in [
                    "dps_enabled",
                    "dps_power_step",
                    "dps_min_power",
                    "dps_shutdown_enabled",
                    "dps_shutdown_duration",
                ]
            ]
        ):
            cfg["power_scaling"] = {}
            if self.dps_enabled:
                cfg["power_scaling"]["enabled"] = self.dps_enabled
            if self.dps_power_step:
                cfg["power_scaling"]["power_step"] = self.dps_power_step
            if self.dps_min_power:
                cfg["power_scaling"]["min_psu_power_limit"] = self.dps_min_power
            if self.dps_shutdown_enabled:
                cfg["power_scaling"]["shutdown_enabled"] = self.dps_shutdown_enabled
            if self.dps_shutdown_duration:
                cfg["power_scaling"]["shutdown_duration"] = self.dps_shutdown_duration

        return toml.dumps(cfg)
