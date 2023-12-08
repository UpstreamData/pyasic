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

from pyasic.config.base import MinerConfigOption, MinerConfigValue


@dataclass
class MiningModeNormal(MinerConfigValue):
    mode: str = field(init=False, default="normal")

    def as_am_modern(self):
        return {"miner-mode": "0"}

    def as_wm(self):
        return {"mode": self.mode}


@dataclass
class MiningModeSleep(MinerConfigValue):
    mode: str = field(init=False, default="sleep")

    def as_am_modern(self):
        return {"miner-mode": "1"}

    def as_wm(self):
        return {"mode": self.mode}


@dataclass
class MiningModeLPM(MinerConfigValue):
    mode: str = field(init=False, default="low")

    def as_am_modern(self):
        return {"miner-mode": "3"}

    def as_wm(self):
        return {"mode": self.mode}


@dataclass
class MiningModeHPM(MinerConfigValue):
    mode: str = field(init=False, default="high")

    def as_am_modern(self):
        return {"miner-mode": "0"}

    def as_wm(self):
        return {"mode": self.mode}


@dataclass
class MiningModePowerTune(MinerConfigValue):
    mode: str = field(init=False, default="power_tuning")
    power: int

    def as_am_modern(self):
        return {"miner-mode": "0"}

    def as_wm(self):
        return {"mode": self.mode, self.mode: {"wattage": self.power}}


@dataclass
class MiningModeHashrateTune(MinerConfigValue):
    mode: str = field(init=False, default="hashrate_tuning")
    hashrate: int

    def as_am_modern(self):
        return {"miner-mode": "0"}


@dataclass
class ManualBoardSettings(MinerConfigValue):
    freq: float
    volt: float

    def as_am_modern(self):
        return {"miner-mode": "0"}


@dataclass
class MiningModeManual(MinerConfigValue):
    mode: str = field(init=False, default="manual")

    global_freq: float
    global_volt: float
    boards: dict[int, ManualBoardSettings] = field(default_factory=dict)

    def as_am_modern(self):
        return {"miner-mode": "0"}


class MiningModeConfig(MinerConfigOption):
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
