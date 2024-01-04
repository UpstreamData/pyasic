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
from typing import Dict, Union

from pyasic.config.base import MinerConfigOption, MinerConfigValue


@dataclass
class MiningModeNormal(MinerConfigValue):
    mode: str = field(init=False, default="normal")

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "MiningModeNormal":
        return cls()

    def as_am_modern(self) -> dict:
        return {"miner-mode": "0"}

    def as_wm(self) -> dict:
        return {"mode": self.mode}


@dataclass
class MiningModeSleep(MinerConfigValue):
    mode: str = field(init=False, default="sleep")

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "MiningModeSleep":
        return cls()

    def as_am_modern(self) -> dict:
        return {"miner-mode": "1"}

    def as_wm(self) -> dict:
        return {"mode": self.mode}


@dataclass
class MiningModeLPM(MinerConfigValue):
    mode: str = field(init=False, default="low")

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "MiningModeLPM":
        return cls()

    def as_am_modern(self) -> dict:
        return {"miner-mode": "3"}

    def as_wm(self) -> dict:
        return {"mode": self.mode}


@dataclass
class MiningModeHPM(MinerConfigValue):
    mode: str = field(init=False, default="high")

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "MiningModeHPM":
        return cls()

    def as_am_modern(self):
        return {"miner-mode": "0"}

    def as_wm(self) -> dict:
        return {"mode": self.mode}


@dataclass
class MiningModePowerTune(MinerConfigValue):
    mode: str = field(init=False, default="power_tuning")
    power: int = None

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "MiningModePowerTune":
        return cls(dict_conf.get("power"))

    def as_am_modern(self) -> dict:
        return {"miner-mode": "0"}

    def as_wm(self) -> dict:
        if self.power is not None:
            return {"mode": self.mode, self.mode: {"wattage": self.power}}
        return {}

    def as_bosminer(self) -> dict:
        return {"autotuning": {"enabled": True, "psu_power_limit": self.power}}


@dataclass
class MiningModeHashrateTune(MinerConfigValue):
    mode: str = field(init=False, default="hashrate_tuning")
    hashrate: int = None

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "MiningModeHashrateTune":
        return cls(dict_conf.get("hashrate"))

    def as_am_modern(self) -> dict:
        return {"miner-mode": "0"}


@dataclass
class ManualBoardSettings(MinerConfigValue):
    freq: float
    volt: float

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "ManualBoardSettings":
        return cls(freq=dict_conf["freq"], volt=dict_conf["volt"])

    def as_am_modern(self) -> dict:
        return {"miner-mode": "0"}


@dataclass
class MiningModeManual(MinerConfigValue):
    mode: str = field(init=False, default="manual")

    global_freq: float
    global_volt: float
    boards: Dict[int, ManualBoardSettings] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "MiningModeManual":
        return cls(
            global_freq=dict_conf["global_freq"],
            global_volt=dict_conf["global_volt"],
            boards={i: ManualBoardSettings.from_dict(dict_conf[i]) for i in dict_conf},
        )

    def as_am_modern(self) -> dict:
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

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]):
        if dict_conf is None:
            return cls.default()

        mode = dict_conf.get("mode")
        if mode is None:
            return cls.default()

        clsattr = getattr(cls, mode)
        if clsattr is not None:
            return clsattr().from_dict(dict_conf)

    @classmethod
    def from_am_modern(cls, web_conf: dict):
        if web_conf.get("bitmain-work-mode") is not None:
            work_mode = web_conf["bitmain-work-mode"]
            if work_mode == "":
                return cls.default()
            if int(work_mode) == 0:
                return cls.normal()
            elif int(work_mode) == 1:
                return cls.sleep()
            elif int(work_mode) == 3:
                return cls.low()
        return cls.default()

    @classmethod
    def from_epic(cls, web_conf: dict):
        try:
            work_mode = web_conf["PerpetualTune"]["Running"]
            if work_mode:
                if (
                    web_conf["PerpetualTune"]["Algorithm"].get("VoltageOptimizer")
                    is not None
                ):
                    return cls.hashrate_tuning(
                        web_conf["PerpetualTune"]["Algorithm"]["VoltageOptimizer"][
                            "Target"
                        ]
                    )
                else:
                    return cls.hashrate_tuning(
                        web_conf["PerpetualTune"]["Algorithm"]["ChipTune"]["Target"]
                    )
            else:
                return cls.normal()
        except KeyError:
            return cls.default()

    @classmethod
    def from_bosminer(cls, toml_conf: dict):
        if toml_conf.get("autotuning") is None:
            return cls.default()
        autotuning_conf = toml_conf["autotuning"]

        if autotuning_conf.get("enabled") is None:
            return cls.default()
        if not autotuning_conf["enabled"]:
            return cls.default()

        if autotuning_conf.get("psu_power_limit") is not None:
            # old autotuning conf
            return cls.power_tuning(autotuning_conf["psu_power_limit"])
        if autotuning_conf.get("mode") is not None:
            # new autotuning conf
            mode = autotuning_conf["mode"]
            if mode == "power_target":
                if autotuning_conf.get("power_target") is not None:
                    return cls.power_tuning(autotuning_conf["power_target"])
                return cls.power_tuning()
            if mode == "hashrate_target":
                if autotuning_conf.get("hashrate_target") is not None:
                    return cls.hashrate_tuning(autotuning_conf["hashrate_target"])
                return cls.hashrate_tuning()
