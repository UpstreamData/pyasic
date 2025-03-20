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

from typing import TypeVar, Union

from pydantic import Field

from pyasic.config.base import MinerConfigOption, MinerConfigValue


class FanModeNormal(MinerConfigValue):
    mode: str = Field(init=False, default="normal")
    minimum_fans: int = 1
    minimum_speed: int = 0

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "FanModeNormal":
        cls_conf = {}
        if dict_conf.get("minimum_fans") is not None:
            cls_conf["minimum_fans"] = dict_conf["minimum_fans"]
        if dict_conf.get("minimum_speed") is not None:
            cls_conf["minimum_speed"] = dict_conf["minimum_speed"]
        return cls(**cls_conf)

    @classmethod
    def from_vnish(cls, web_cooling_settings: dict) -> "FanModeNormal":
        cls_conf = {}
        if web_cooling_settings.get("fan_min_count") is not None:
            cls_conf["minimum_fans"] = web_cooling_settings["fan_min_count"]
        if web_cooling_settings.get("fan_min_duty") is not None:
            cls_conf["minimum_speed"] = web_cooling_settings["fan_min_duty"]
        return cls(**cls_conf)

    @classmethod
    def from_bosminer(cls, toml_fan_conf: dict):
        cls_conf = {}
        if toml_fan_conf.get("min_fans") is not None:
            cls_conf["minimum_fans"] = toml_fan_conf["min_fans"]
        return cls(**cls_conf)

    def as_am_modern(self) -> dict:
        return {"bitmain-fan-ctrl": False, "bitmain-fan-pwn": "100"}

    def as_hiveon_modern(self) -> dict:
        return {"bitmain-fan-ctrl": False, "bitmain-fan-pwn": "100"}

    def as_elphapex(self) -> dict:
        return {"fc-fan-ctrl": False, "fc-fan-pwn": "100"}

    def as_bosminer(self) -> dict:
        return {
            "temp_control": {"mode": "auto"},
            "fan_control": {"min_fans": self.minimum_fans},
        }

    def as_epic(self) -> dict:
        return {
            "fans": {
                "Auto": {
                    "Idle Speed": (
                        self.minimum_speed if not self.minimum_speed == 0 else 100
                    )
                }
            }
        }

    def as_mara(self) -> dict:
        return {
            "general-config": {"environment-profile": "AirCooling"},
            "advance-config": {
                "override-fan-control": False,
                "fan-fixed-percent": 0,
            },
        }

    def as_espminer(self) -> dict:
        return {"autoFanspeed": 1}

    def as_luxos(self) -> dict:
        return {"fanset": {"speed": -1, "min_fans": self.minimum_fans}}

    def as_vnish(self) -> dict:
        return {
            "cooling": {
                "fan_min_count": self.minimum_fans,
                "fan_min_duty": self.minimum_speed,
                "mode": {
                    "name": "auto",
                    "param": None,  # Target temp, must be set later...
                },
            }
        }


class FanModeManual(MinerConfigValue):
    mode: str = Field(init=False, default="manual")
    speed: int = 100
    minimum_fans: int = 1

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "FanModeManual":
        cls_conf = {}
        if dict_conf.get("speed") is not None:
            cls_conf["speed"] = dict_conf["speed"]
        if dict_conf.get("minimum_fans") is not None:
            cls_conf["minimum_fans"] = dict_conf["minimum_fans"]
        return cls(**cls_conf)

    @classmethod
    def from_bosminer(cls, toml_fan_conf: dict) -> "FanModeManual":
        cls_conf = {}
        if toml_fan_conf.get("min_fans") is not None:
            cls_conf["minimum_fans"] = toml_fan_conf["min_fans"]
        if toml_fan_conf.get("speed") is not None:
            cls_conf["speed"] = toml_fan_conf["speed"]
        return cls(**cls_conf)

    @classmethod
    def from_vnish(cls, web_cooling_settings: dict) -> "FanModeManual":
        cls_conf = {}
        if web_cooling_settings.get("fan_min_count") is not None:
            cls_conf["minimum_fans"] = web_cooling_settings["fan_min_count"]
        if web_cooling_settings["mode"].get("param") is not None:
            cls_conf["speed"] = web_cooling_settings["mode"]["param"]
        return cls(**cls_conf)

    def as_am_modern(self) -> dict:
        return {"bitmain-fan-ctrl": True, "bitmain-fan-pwm": str(self.speed)}

    def as_hiveon_modern(self) -> dict:
        return {"bitmain-fan-ctrl": True, "bitmain-fan-pwm": str(self.speed)}

    def as_elphapex(self) -> dict:
        return {"fc-fan-ctrl": True, "fc-fan-pwm": str(self.speed)}

    def as_bosminer(self) -> dict:
        return {
            "temp_control": {"mode": "manual"},
            "fan_control": {"min_fans": self.minimum_fans, "speed": self.speed},
        }

    def as_auradine(self) -> dict:
        return {"fan": {"percentage": self.speed}}

    def as_epic(self) -> dict:
        return {"fans": {"Manual": {"speed": self.speed}}}

    def as_mara(self) -> dict:
        return {
            "general-config": {"environment-profile": "AirCooling"},
            "advance-config": {
                "override-fan-control": True,
                "fan-fixed-percent": self.speed,
            },
        }

    def as_espminer(self) -> dict:
        return {"autoFanspeed": 0, "fanspeed": self.speed}

    def as_luxos(self) -> dict:
        return {"fanset": {"speed": self.speed, "min_fans": self.minimum_fans}}

    def as_vnish(self) -> dict:
        return {
            "cooling": {
                "fan_min_count": self.minimum_fans,
                "fan_min_duty": self.speed,
                "mode": {
                    "name": "manual",
                    "param": self.speed,  # Speed value
                },
            }
        }


class FanModeImmersion(MinerConfigValue):
    mode: str = Field(init=False, default="immersion")

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "FanModeImmersion":
        return cls()

    def as_am_modern(self) -> dict:
        return {"bitmain-fan-ctrl": True, "bitmain-fan-pwm": "0"}

    def as_hiveon_modern(self) -> dict:
        return {"bitmain-fan-ctrl": True, "bitmain-fan-pwm": "0"}

    def as_elphapex(self) -> dict:
        return {"fc-fan-ctrl": True, "fc-fan-pwm": "0"}

    def as_bosminer(self) -> dict:
        return {
            "fan_control": {"min_fans": 0},
        }

    def as_auradine(self) -> dict:
        return {"fan": {"percentage": 0}}

    def as_mara(self) -> dict:
        return {"general-config": {"environment-profile": "OilImmersionCooling"}}

    def as_luxos(self) -> dict:
        return {"fanset": {"speed": 0, "min_fans": 0}}

    def as_vnish(self) -> dict:
        return {"cooling": {"mode": {"name": "immers"}}}


class FanModeConfig(MinerConfigOption):
    normal = FanModeNormal
    manual = FanModeManual
    immersion = FanModeImmersion

    @classmethod
    def default(cls):
        return cls.normal()

    @classmethod
    def from_dict(cls, dict_conf: dict | None):
        if dict_conf is None:
            return cls.default()

        mode = dict_conf.get("mode")
        if mode is None:
            return cls.default()

        cls_attr = getattr(cls, mode)
        if cls_attr is not None:
            return cls_attr().from_dict(dict_conf)

    @classmethod
    def from_am_modern(cls, web_conf: dict):
        if web_conf.get("bitmain-fan-ctrl") is not None:
            fan_manual = web_conf["bitmain-fan-ctrl"]
            if fan_manual:
                speed = int(web_conf["bitmain-fan-pwm"])
                if speed == 0:
                    return cls.immersion()
                return cls.manual(speed=speed)
            else:
                return cls.normal()
        else:
            return cls.default()

    @classmethod
    def from_hiveon_modern(cls, web_conf: dict):
        if web_conf.get("bitmain-fan-ctrl") is not None:
            fan_manual = web_conf["bitmain-fan-ctrl"]
            if fan_manual:
                speed = int(web_conf["bitmain-fan-pwm"])
                if speed == 0:
                    return cls.immersion()
                return cls.manual(speed=speed)
            else:
                return cls.normal()
        else:
            return cls.default()

    @classmethod
    def from_elphapex(cls, web_conf: dict):
        if web_conf.get("fc-fan-ctrl") is not None:
            fan_manual = web_conf["fc-fan-ctrl"]
            if fan_manual:
                speed = int(web_conf["fc-fan-pwm"])
                if speed == 0:
                    return cls.immersion()
                return cls.manual(speed=speed)
            else:
                return cls.normal()
        else:
            return cls.default()

    @classmethod
    def from_epic(cls, web_conf: dict):
        try:
            fan_mode = web_conf["Fans"]["Fan Mode"]
            if fan_mode.get("Manual") is not None:
                return cls.manual(speed=fan_mode.get("Manual"))
            else:
                return cls.normal()
        except KeyError:
            return cls.default()

    @classmethod
    def from_bosminer(cls, toml_conf: dict):
        try:
            mode = toml_conf["temp_control"]["mode"]
            fan_config = toml_conf.get("fan_control", {})
            if mode == "auto":
                return cls.normal().from_bosminer(fan_config)
            elif mode == "manual":
                if toml_conf.get("fan_control"):
                    return cls.manual().from_bosminer(fan_config)
                return cls.manual()
            elif mode == "disabled":
                return cls.immersion()
        except KeyError:
            pass

        try:
            min_fans = toml_conf["fan_control"]["min_fans"]
        except KeyError:
            return cls.default()

        if min_fans == 0:
            return cls.immersion()
        return cls.normal(minimum_fans=min_fans)

    @classmethod
    def from_vnish(cls, web_settings: dict):
        try:
            mode = web_settings["miner"]["cooling"]["mode"]["name"]
        except LookupError:
            return cls.default()

        if mode == "auto":
            return cls.normal().from_vnish(web_settings["miner"]["cooling"])
        elif mode == "manual":
            return cls.manual().from_vnish(web_settings["miner"]["cooling"])
        elif mode == "immers":
            return cls.immersion()

    @classmethod
    def from_boser(cls, grpc_miner_conf: dict):
        try:
            temperature_conf = grpc_miner_conf["temperature"]
        except LookupError:
            return cls.default()

        keys = temperature_conf.keys()
        if "auto" in keys:
            if "minimumRequiredFans" in keys:
                return cls.normal(minimum_fans=temperature_conf["minimumRequiredFans"])
            return cls.normal()
        if "manual" in keys:
            conf = {}
            if "fanSpeedRatio" in temperature_conf["manual"].keys():
                conf["speed"] = int(temperature_conf["manual"]["fanSpeedRatio"])
            if "minimumRequiredFans" in keys:
                conf["minimum_fans"] = int(temperature_conf["minimumRequiredFans"])
            return cls.manual(**conf)
        if "disabled" in keys:
            conf = {}
            if "fanSpeedRatio" in temperature_conf["disabled"].keys():
                conf["speed"] = int(temperature_conf["disabled"]["fanSpeedRatio"])
            return cls.manual(**conf)
        return cls.default()

    @classmethod
    def from_auradine(cls, web_fan: dict):
        try:
            fan_data = web_fan["Fan"][0]
            fan_1_max = fan_data["Max"]
            fan_1_target = fan_data["Target"]
            return cls.manual(speed=round((fan_1_target / fan_1_max) * 100))
        except LookupError:
            pass
        return cls.default()

    @classmethod
    def from_mara(cls, web_config: dict):
        try:
            mode = web_config["general-config"]["environment-profile"]
            if mode == "AirCooling":
                if web_config["advance-config"]["override-fan-control"]:
                    return cls.manual(
                        speed=web_config["advance-config"]["fan-fixed-percent"]
                    )
                return cls.normal()
            return cls.immersion()
        except LookupError:
            pass
        return cls.default()

    @classmethod
    def from_espminer(cls, web_system_info: dict):
        if web_system_info["autofanspeed"] == 1:
            return cls.normal()
        else:
            return cls.manual(speed=web_system_info["fanspeed"])

    @classmethod
    def from_luxos(cls, rpc_fans: dict, rpc_tempctrl: dict):
        try:
            mode = rpc_tempctrl["TEMPCTRL"][0]["Mode"]
            if mode == "Manual":
                speed = rpc_fans["FANS"][0]["Speed"]
                min_fans = rpc_fans["FANCTRL"][0]["MinFans"]
                if min_fans == 0 and speed == 0:
                    return cls.immersion()
                return cls.manual(
                    speed=speed,
                    minimum_fans=min_fans,
                )
            return cls.normal(
                minimum_fans=rpc_fans["FANCTRL"][0]["MinFans"],
            )
        except LookupError:
            pass
        return cls.default()


FanMode = TypeVar(
    "FanMode",
    bound=Union[FanModeNormal, FanModeManual, FanModeImmersion],
)
