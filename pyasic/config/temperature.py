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

from dataclasses import dataclass

from pyasic.config.base import MinerConfigValue


@dataclass
class TemperatureConfig(MinerConfigValue):
    target: int = None
    hot: int = None
    danger: int = None

    @classmethod
    def default(cls):
        return cls()

    def as_bosminer(self) -> dict:
        temp_cfg = {}
        if self.target is not None:
            temp_cfg["target_temp"] = self.target
        if self.hot is not None:
            temp_cfg["hot_temp"] = self.hot
        if self.danger is not None:
            temp_cfg["dangerous_temp"] = self.danger
        if len(temp_cfg) == 0:
            return {}
        return {"temp_control": temp_cfg}

    def as_epic(self) -> dict:
        temps_config = {"temps": {}, "fans": {"Auto": {}}}
        if self.target is not None:
            temps_config["fans"]["Auto"]["Target Temperature"] = self.target
        else:
            temps_config["fans"]["Auto"]["Target Temperature"] = 60
        if self.danger is not None:
            temps_config["temps"]["critical"] = self.danger
        if self.hot is not None:
            temps_config["temps"]["shutdown"] = self.hot
        return temps_config

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "TemperatureConfig":
        return cls(
            target=dict_conf.get("target"),
            hot=dict_conf.get("hot"),
            danger=dict_conf.get("danger"),
        )

    @classmethod
    def from_bosminer(cls, toml_conf: dict) -> "TemperatureConfig":
        temp_control = toml_conf.get("temp_control")
        if temp_control is not None:
            return cls(
                target=temp_control.get("target_temp"),
                hot=temp_control.get("hot_temp"),
                danger=temp_control.get("dangerous_temp"),
            )
        return cls()

    @classmethod
    def from_epic(cls, web_conf: dict) -> "TemperatureConfig":
        try:
            dangerous_temp = web_conf["Misc"]["Critical Temp"]
        except KeyError:
            dangerous_temp = None
        try:
            hot_temp = web_conf["Misc"]["Shutdown Temp"]
        except KeyError:
            hot_temp = None
        # Need to do this in two blocks to avoid KeyError if one is missing
        try:
            target_temp = web_conf["Fans"]["Fan Mode"]["Auto"]["Target Temperature"]
        except KeyError:
            target_temp = None

        return cls(target=target_temp, hot=hot_temp, danger=dangerous_temp)

    @classmethod
    def from_vnish(cls, web_settings: dict) -> "TemperatureConfig":
        try:
            if web_settings["miner"]["cooling"]["mode"]["name"] == "auto":
                return cls(target=web_settings["miner"]["cooling"]["mode"]["param"])
        except KeyError:
            pass
        return cls()

    @classmethod
    def from_boser(cls, grpc_miner_conf: dict) -> "TemperatureConfig":
        try:
            temperature_conf = grpc_miner_conf["temperature"]
        except KeyError:
            return cls.default()

        root_key = None
        for key in ["auto", "manual", "disabled"]:
            if key in temperature_conf.keys():
                root_key = key
                break
        if root_key is None:
            return cls.default()

        conf = {}
        keys = temperature_conf[root_key].keys()
        if "targetTemperature" in keys:
            conf["target"] = int(
                temperature_conf[root_key]["targetTemperature"]["degreeC"]
            )
        if "hotTemperature" in keys:
            conf["hot"] = int(temperature_conf[root_key]["hotTemperature"]["degreeC"])
        if "dangerousTemperature" in keys:
            conf["danger"] = int(
                temperature_conf[root_key]["dangerousTemperature"]["degreeC"]
            )

            return cls(**conf)
        return cls.default()
