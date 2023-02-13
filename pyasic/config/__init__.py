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

import json
import logging
import random
import string
import time
from dataclasses import asdict, dataclass, fields
from typing import Dict, List, Literal

import toml
import yaml


@dataclass
class _Pool:
    """A dataclass for pool information.

    Attributes:
        url: URL of the pool.
        username: Username on the pool.
        password: Worker password on the pool.
    """

    url: str = ""
    username: str = ""
    password: str = ""

    @classmethod
    def fields(cls):
        return fields(cls)

    def from_dict(self, data: dict):
        """Convert raw pool data as a dict to usable data and save it to this class.

        Parameters:
             data: The raw config data to convert.
        """
        for key in data.keys():
            if key == "url":
                self.url = data[key]
            if key in ["user", "username"]:
                self.username = data[key]
            if key in ["pass", "password"]:
                self.password = data[key]
        return self

    def as_wm(self, user_suffix: str = None) -> dict:
        """Convert the data in this class to a dict usable by an Whatsminer device.

        Parameters:
             user_suffix: The suffix to append to username.
        """
        username = self.username
        if user_suffix:
            username = f"{username}{user_suffix}"

        pool = {"url": self.url, "user": username, "pass": self.password}
        return pool

    def as_x19(self, user_suffix: str = None) -> dict:
        """Convert the data in this class to a dict usable by an X19 device.

        Parameters:
             user_suffix: The suffix to append to username.
        """
        username = self.username
        if user_suffix:
            username = f"{username}{user_suffix}"

        pool = {"url": self.url, "user": username, "pass": self.password}
        return pool

    def as_inno(self, user_suffix: str = None) -> dict:
        """Convert the data in this class to a dict usable by an Innosilicon device.

        Parameters:
             user_suffix: The suffix to append to username.
        """
        username = self.username
        if user_suffix:
            username = f"{username}{user_suffix}"

        pool = {
            f"Pool": self.url,
            f"UserName": username,
            f"Password": self.password,
        }
        return pool

    def as_avalon(self, user_suffix: str = None) -> str:
        """Convert the data in this class to a string usable by an Avalonminer device.

        Parameters:
             user_suffix: The suffix to append to username.
        """
        username = self.username
        if user_suffix:
            username = f"{username}{user_suffix}"

        pool = ",".join([self.url, username, self.password])
        return pool

    def as_bos(self, user_suffix: str = None) -> dict:
        """Convert the data in this class to a dict usable by an BOSMiner device.

        Parameters:
            user_suffix: The suffix to append to username.
        """
        username = self.username
        if user_suffix:
            username = f"{username}{user_suffix}"

        pool = {"url": self.url, "user": username, "password": self.password}
        return pool


@dataclass
class _PoolGroup:
    """A dataclass for pool group information.

    Attributes:
        quota: The group quota.
        group_name: The name of the pool group.
        pools: A list of pools in this group.
    """

    quota: int = 1
    group_name: str = None
    pools: List[_Pool] = None

    @classmethod
    def fields(cls):
        return fields(cls)

    def __post_init__(self):
        if not self.group_name:
            self.group_name = "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
            )  # generate random pool group name in case it isn't set

    def from_dict(self, data: dict):
        """Convert raw pool group data as a dict to usable data and save it to this class.

        Parameters:
             data: The raw config data to convert.
        """
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

    def as_x19(self, user_suffix: str = None) -> List[dict]:
        """Convert the data in this class to a list usable by an X19 device.

        Parameters:
             user_suffix: The suffix to append to username.
        """
        pools = []
        for pool in self.pools[:3]:
            pools.append(pool.as_x19(user_suffix=user_suffix))
        return pools

    def as_inno(self, user_suffix: str = None) -> dict:
        """Convert the data in this class to a list usable by an Innosilicon device.

        Parameters:
             user_suffix: The suffix to append to username.
        """
        pools = {}
        for idx, pool in enumerate(self.pools[:3]):
            pool_data = pool.as_inno(user_suffix=user_suffix)
            for key in pool_data:
                pools[f"{key}{idx+1}"] = pool_data[key]
        return pools

    def as_wm(self, user_suffix: str = None) -> List[dict]:
        """Convert the data in this class to a list usable by a Whatsminer device.

        Parameters:
             user_suffix: The suffix to append to username.
        """
        pools = []
        for pool in self.pools[:3]:
            pools.append(pool.as_wm(user_suffix=user_suffix))
        while len(pools) < 3:
            pools.append({"url": None, "user": None, "pass": None})
        return pools

    def as_avalon(self, user_suffix: str = None) -> str:
        """Convert the data in this class to a dict usable by an Avalonminer device.

        Parameters:
             user_suffix: The suffix to append to username.
        """
        pool = self.pools[0].as_avalon(user_suffix=user_suffix)
        return pool

    def as_bos(self, user_suffix: str = None) -> dict:
        """Convert the data in this class to a dict usable by an BOSMiner device.

        Parameters:
             user_suffix: The suffix to append to username.
        """
        group = {
            "name": self.group_name,
            "quota": self.quota,
            "pool": [pool.as_bos(user_suffix=user_suffix) for pool in self.pools],
        }
        return group


@dataclass
class MinerConfig:
    """A dataclass for miner configuration information.

    Attributes:
        pool_groups: A list of pool groups in this config.
        temp_mode: The temperature control mode.
        temp_target: The target temp.
        temp_hot: The hot temp (100% fans).
        temp_dangerous: The dangerous temp (shutdown).
        minimum_fans: The minimum numbers of fans to run the miner.
        fan_speed: Manual fan speed to run the fan at (only if temp_mode == "manual").
        asicboost: Whether or not to enable asicboost.
        autotuning_enabled: Whether or not to enable autotuning.
        autotuning_wattage: The wattage to use when autotuning.
        dps_enabled: Whether or not to enable dynamic power scaling.
        dps_power_step: The amount of power to reduce autotuning by when the miner reaches dangerous temp.
        dps_min_power: The minimum power to reduce autotuning to.
        dps_shutdown_enabled: Whether or not to shutdown the miner when `dps_min_power` is reached.
        dps_shutdown_duration: The amount of time to shutdown for (in hours).
    """

    pool_groups: List[_PoolGroup] = None

    temp_mode: Literal["auto", "manual", "disabled"] = "auto"
    temp_target: float = 70.0
    temp_hot: float = 80.0
    temp_dangerous: float = 100.0

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

    @classmethod
    def fields(cls):
        return fields(cls)

    def as_dict(self) -> dict:
        """Convert the data in this class to a dict."""
        logging.debug(f"MinerConfig - (To Dict) - Dumping Dict config")
        data_dict = asdict(self)
        for key in asdict(self).keys():
            if data_dict[key] is None:
                del data_dict[key]
        return data_dict

    def as_toml(self) -> str:
        """Convert the data in this class to toml."""
        logging.debug(f"MinerConfig - (To TOML) - Dumping TOML config")
        return toml.dumps(self.as_dict())

    def as_yaml(self) -> str:
        """Convert the data in this class to yaml."""
        logging.debug(f"MinerConfig - (To YAML) - Dumping YAML config")
        return yaml.dump(self.as_dict(), sort_keys=False)

    def from_raw(self, data: dict):
        """Convert raw config data as a dict to usable data and save it to this class.
        This should be able to handle any raw config file from any miner supported by pyasic.

        Parameters:
             data: The raw config data to convert.
        """
        logging.debug(f"MinerConfig - (From Raw) - Loading raw config")
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
            elif key == "bitmain-work-mode":
                if data[key]:
                    if data[key] == 1:
                        self.autotuning_wattage = 0
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

    def from_api(self, pools: list):
        """Convert list output from the `AnyMiner.api.pools()` command into a usable data and save it to this class.

        Parameters:
            pools: The list of pool data to convert.
        """
        logging.debug(f"MinerConfig - (From API) - Loading API config")
        _pools = []
        for pool in pools:
            url = pool.get("URL")
            user = pool.get("User")
            _pools.append({"url": url, "user": user, "pass": "123"})
        self.pool_groups = [_PoolGroup().from_dict({"pools": _pools})]
        return self

    def from_dict(self, data: dict):
        """Convert an output dict of this class back into usable data and save it to this class.

        Parameters:
            data: The dict config data to convert.
        """
        logging.debug(f"MinerConfig - (From Dict) - Loading Dict config")
        pool_groups = []
        for group in data["pool_groups"]:
            pool_groups.append(_PoolGroup().from_dict(group))
        for key in data.keys():
            if getattr(self, key) and not key == "pool_groups":
                setattr(self, key, data[key])
        self.pool_groups = pool_groups
        return self

    def from_toml(self, data: str):
        """Convert output toml of this class back into usable data and save it to this class.

        Parameters:
            data: The toml config data to convert.
        """
        logging.debug(f"MinerConfig - (From TOML) - Loading TOML config")
        return self.from_dict(toml.loads(data))

    def from_yaml(self, data: str):
        """Convert output yaml of this class back into usable data and save it to this class.

        Parameters:
            data: The yaml config data to convert.
        """
        logging.debug(f"MinerConfig - (From YAML) - Loading YAML config")
        return self.from_dict(yaml.load(data, Loader=yaml.SafeLoader))

    def as_wm(self, user_suffix: str = None) -> Dict[str, int]:
        """Convert the data in this class to a config usable by a Whatsminer device.

        Parameters:
            user_suffix: The suffix to append to username.
        """
        logging.debug(f"MinerConfig - (As Whatsminer) - Generating Whatsminer config")
        return {
            "pools": self.pool_groups[0].as_wm(user_suffix=user_suffix),
            "wattage": self.autotuning_wattage,
        }

    def as_inno(self, user_suffix: str = None) -> dict:
        """Convert the data in this class to a config usable by an Innosilicon device.

        Parameters:
            user_suffix: The suffix to append to username.
        """
        logging.debug(f"MinerConfig - (As Inno) - Generating Innosilicon config")
        return self.pool_groups[0].as_inno(user_suffix=user_suffix)

    def as_x19(self, user_suffix: str = None) -> str:
        """Convert the data in this class to a config usable by an X19 device.

        Parameters:
            user_suffix: The suffix to append to username.
        """
        logging.debug(f"MinerConfig - (As X19) - Generating X19 config")
        cfg = {
            "pools": self.pool_groups[0].as_x19(user_suffix=user_suffix),
            "bitmain-fan-ctrl": False,
            "bitmain-fan-pwn": 100,
            "miner-mode": 0,  # Normal Mode
        }
        if self.autotuning_wattage == 0:
            cfg["miner-mode"] = 1  # Sleep Mode

        if not self.temp_mode == "auto":
            cfg["bitmain-fan-ctrl"] = True

        if self.fan_speed:
            cfg["bitmain-fan-ctrl"] = str(self.fan_speed)

        return json.dumps(cfg)

    def as_avalon(self, user_suffix: str = None) -> str:
        """Convert the data in this class to a config usable by an Avalonminer device.

        Parameters:
            user_suffix: The suffix to append to username.
        """
        logging.debug(f"MinerConfig - (As Avalon) - Generating AvalonMiner config")
        cfg = self.pool_groups[0].as_avalon(user_suffix=user_suffix)
        return cfg

    def as_bos(self, model: str = "S9", user_suffix: str = None) -> str:
        """Convert the data in this class to a config usable by an BOSMiner device.

        Parameters:
            model: The model of the miner to be used in the format portion of the config.
            user_suffix: The suffix to append to username.
        """
        logging.debug(f"MinerConfig - (As BOS) - Generating BOSMiner config")
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
