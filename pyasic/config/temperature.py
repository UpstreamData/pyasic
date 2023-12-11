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
from dataclasses import dataclass
from typing import Union

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
        return {"temp_control": temp_cfg}

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "TemperatureConfig":
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
