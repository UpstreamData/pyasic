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
class MiningModeNormal:
    mode: str = field(init=False, default="normal")

    @staticmethod
    def as_am_modern():
        return {"miner-mode": "0"}


@dataclass
class MiningModeSleep:
    mode: str = field(init=False, default="sleep")

    @staticmethod
    def as_am_modern():
        return {"miner-mode": "1"}


@dataclass
class MiningModeLPM:
    mode: str = field(init=False, default="low")

    @staticmethod
    def as_am_modern():
        return {"miner-mode": "3"}


@dataclass
class MiningModeHPM(MiningModeNormal):
    mode: str = field(init=False, default="high")


@dataclass
class MiningModePowerTune(MiningModeNormal):
    mode: str = field(init=False, default="power_tuning")
    power: int


@dataclass
class MiningModeHashrateTune(MiningModeNormal):
    mode: str = field(init=False, default="hashrate_tuning")
    hashrate: int


@dataclass
class ManualBoardSettings:
    freq: float
    volt: float


@dataclass
class MiningModeManual(MiningModeNormal):
    mode: str = field(init=False, default="manual")

    global_freq: float
    global_volt: float
    boards: dict[int, ManualBoardSettings] = field(default_factory=dict)


class MiningModeConfig(Enum):
    normal = MiningModeNormal
    low = MiningModeLPM
    high = MiningModeHPM
    sleep = MiningModeSleep
    power_tuning = MiningModePowerTune
    hashrate_tuning = MiningModeHashrateTune
    manual = MiningModeManual

    @classmethod
    def default(cls):
        return cls.normal()

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)
