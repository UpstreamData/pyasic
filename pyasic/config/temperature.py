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

from pyasic.config.base import MinerConfigValue


class TemperatureConfig(MinerConfigValue):
    target: int | None = None
    hot: int | None = None
    danger: int | None = None

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
        temps_config: dict = {"temps": {}, "fans": {"Auto": {}}}
        if self.target is not None:
            temps_config["fans"]["Auto"]["Target Temperature"] = self.target
        else:
            temps_config["fans"]["Auto"]["Target Temperature"] = 60
        if self.danger is not None:
            temps_config["temps"]["critical"] = self.danger
        if self.hot is not None:
            temps_config["temps"]["shutdown"] = self.hot
        return temps_config

    def as_luxos(self) -> dict:
        return {"tempctrlset": [self.target or "", self.hot or "", self.danger or ""]}

    def as_vnish(self) -> dict:
        return {"misc": {"restart_temp": self.danger}}

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> TemperatureConfig:
        if dict_conf is None:
            return cls()
        return cls(
            target=dict_conf.get("target"),
            hot=dict_conf.get("hot"),
            danger=dict_conf.get("danger"),
        )

    @classmethod
    def from_bosminer(cls, toml_conf: dict) -> TemperatureConfig:
        temp_control = toml_conf.get("temp_control")
        if temp_control is not None:
            return cls(
                target=temp_control.get("target_temp"),
                hot=temp_control.get("hot_temp"),
                danger=temp_control.get("dangerous_temp"),
            )
        return cls()

    @classmethod
    def from_epic(cls, web_conf: dict) -> TemperatureConfig:
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
    def from_vnish(cls, web_settings: dict) -> TemperatureConfig:
        try:
            dangerous_temp = web_settings["misc"]["restart_temp"]
        except KeyError:
            dangerous_temp = None
        try:
            if web_settings["miner"]["cooling"]["mode"]["name"] == "auto":
                return cls(
                    target=web_settings["miner"]["cooling"]["mode"]["param"],
                    danger=dangerous_temp,
                )
        except KeyError:
            pass
        return cls()

    @classmethod
    def from_boser(cls, grpc_miner_conf: dict) -> TemperatureConfig:
        temperature_conf = grpc_miner_conf.get("temperature")
        if not isinstance(temperature_conf, dict):
            return cls.default()

        root_key = None
        for key in ["auto", "manual", "disabled"]:
            if key in temperature_conf:
                root_key = key
                break
        if root_key is None:
            return cls.default()

        raw_conf = temperature_conf.get(root_key) or {}
        if not isinstance(raw_conf, dict):
            return cls.default()

        def _read_temp(temp_block: object) -> int | None:
            if isinstance(temp_block, dict):
                temp_value = temp_block.get("degreeC")
            else:
                temp_value = temp_block
            try:
                return int(temp_value) if temp_value is not None else None
            except (TypeError, ValueError):
                return None

        conf: dict = {}
        target_temp = _read_temp(raw_conf.get("targetTemperature"))
        if target_temp is not None:
            conf["target"] = target_temp
        hot_temp = _read_temp(raw_conf.get("hotTemperature"))
        if hot_temp is not None:
            conf["hot"] = hot_temp
        danger_temp = _read_temp(raw_conf.get("dangerousTemperature"))
        if danger_temp is not None:
            conf["danger"] = danger_temp

        if conf:
            return cls(**conf)
        return cls.default()

    @classmethod
    def from_luxos(cls, rpc_tempctrl: dict) -> TemperatureConfig:
        try:
            tempctrl_config = rpc_tempctrl["TEMPCTRL"][0]
            return cls(
                target=tempctrl_config.get("Target"),
                hot=tempctrl_config.get("Hot"),
                danger=tempctrl_config.get("Dangerous"),
            )
        except LookupError:
            pass
        return cls.default()
