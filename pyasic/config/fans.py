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
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class FanModeNormal:
    mode: str = field(init=False, default="auto")

    @staticmethod
    def as_am_modern():
        return {"bitmain-fan-ctrl": False, "bitmain-fan-pwn": "100"}

    @staticmethod
    def as_bos():
        return {"temp_control": {"mode": "auto"}}


@dataclass
class FanModeManual:
    mode: str = field(init=False, default="manual")
    minimum_fans: int = 1
    speed: int = 100

    def as_am_modern(self):
        return {"bitmain-fan-ctrl": True, "bitmain-fan-pwn": str(self.speed)}

    def as_bos(self):
        return {
            "temp_control": {"mode": "manual"},
            "fan_control": {"min_fans": self.minimum_fans, "speed": self.speed},
        }


@dataclass
class FanModeImmersion:
    mode: str = field(init=False, default="immersion")

    @staticmethod
    def as_am_modern():
        return {"bitmain-fan-ctrl": True, "bitmain-fan-pwn": "0"}

    @staticmethod
    def as_bos():
        return {"temp_control": {"mode": "manual"}, "fan_control": {"min_fans": 0}}


class FanModeConfig(Enum):
    normal = FanModeNormal
    manual = FanModeManual
    immersion = FanModeImmersion

    @classmethod
    def default(cls):
        return cls.normal()

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)
