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

from dataclasses import dataclass, field

from pyasic.config.base import MinerConfigOption, MinerConfigValue
from pyasic.web.braiins_os.proto.braiins.bos.v1 import (
    DpsPowerTarget,
    DpsTarget,
    Power,
    SetDpsRequest,
)


@dataclass
class PowerScalingShutdownEnabled(MinerConfigValue):
    mode: str = field(init=False, default="enabled")
    duration: int = None

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "PowerScalingShutdownEnabled":
        return cls(duration=dict_conf.get("duration"))

    def as_bosminer(self) -> dict:
        cfg = {"shutdown_enabled": True}

        if self.duration is not None:
            cfg["shutdown_duration"] = self.duration

        return cfg

    def as_boser(self) -> dict:
        return {"enable_shutdown": True, "shutdown_duration": self.duration}


@dataclass
class PowerScalingShutdownDisabled(MinerConfigValue):
    mode: str = field(init=False, default="disabled")

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "PowerScalingShutdownDisabled":
        return cls()

    def as_bosminer(self) -> dict:
        return {"shutdown_enabled": False}

    def as_boser(self) -> dict:
        return {"enable_shutdown ": False}


class PowerScalingShutdown(MinerConfigOption):
    enabled = PowerScalingShutdownEnabled
    disabled = PowerScalingShutdownDisabled

    @classmethod
    def from_dict(cls, dict_conf: dict | None):
        if dict_conf is None:
            return cls.default()

        mode = dict_conf.get("mode")
        if mode is None:
            return cls.default()

        clsattr = getattr(cls, mode)
        if clsattr is not None:
            return clsattr().from_dict(dict_conf)

    @classmethod
    def from_bosminer(cls, power_scaling_conf: dict):
        sd_enabled = power_scaling_conf.get("shutdown_enabled")
        if sd_enabled is not None:
            if sd_enabled:
                return cls.enabled(power_scaling_conf.get("shutdown_duration"))
            else:
                return cls.disabled()
        return None

    @classmethod
    def from_boser(cls, power_scaling_conf: dict):
        sd_enabled = power_scaling_conf.get("shutdownEnabled")
        if sd_enabled is not None:
            if sd_enabled:
                try:
                    return cls.enabled(power_scaling_conf["shutdownDuration"]["hours"])
                except KeyError:
                    return cls.enabled()
            else:
                return cls.disabled()
        return None


@dataclass
class PowerScalingEnabled(MinerConfigValue):
    mode: str = field(init=False, default="enabled")
    power_step: int = None
    minimum_power: int = None
    shutdown_enabled: PowerScalingShutdownEnabled | PowerScalingShutdownDisabled = None

    @classmethod
    def from_bosminer(cls, power_scaling_conf: dict) -> "PowerScalingEnabled":
        power_step = power_scaling_conf.get("power_step")
        min_power = power_scaling_conf.get("min_psu_power_limit")
        if min_power is None:
            min_power = power_scaling_conf.get("min_power_target")
        sd_mode = PowerScalingShutdown.from_bosminer(power_scaling_conf)

        return cls(
            power_step=power_step, minimum_power=min_power, shutdown_enabled=sd_mode
        )

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "PowerScalingEnabled":
        cls_conf = {
            "power_step": dict_conf.get("power_step"),
            "minimum_power": dict_conf.get("minimum_power"),
        }
        shutdown_enabled = dict_conf.get("shutdown_enabled")
        if shutdown_enabled is not None:
            cls_conf["shutdown_enabled"] = PowerScalingShutdown.from_dict(
                shutdown_enabled
            )
        return cls(**cls_conf)

    def as_bosminer(self) -> dict:
        cfg = {"enabled": True}
        if self.power_step is not None:
            cfg["power_step"] = self.power_step
        if self.minimum_power is not None:
            cfg["min_power_target"] = self.minimum_power

        if self.shutdown_enabled is not None:
            cfg = {**cfg, **self.shutdown_enabled.as_bosminer()}

        return {"performance_scaling": cfg}

    def as_boser(self) -> dict:
        return {
            "set_dps": SetDpsRequest(
                enable=True,
                **self.shutdown_enabled.as_boser(),
                target=DpsTarget(
                    power_target=DpsPowerTarget(
                        power_step=Power(self.power_step),
                        min_power_target=Power(self.minimum_power),
                    )
                ),
            ),
        }


@dataclass
class PowerScalingDisabled(MinerConfigValue):
    mode: str = field(init=False, default="disabled")


class PowerScalingConfig(MinerConfigOption):
    enabled = PowerScalingEnabled
    disabled = PowerScalingDisabled

    @classmethod
    def default(cls):
        return cls.disabled()

    @classmethod
    def from_dict(cls, dict_conf: dict | None):
        if dict_conf is None:
            return cls.default()

        mode = dict_conf.get("mode")
        if mode is None:
            return cls.default()

        clsattr = getattr(cls, mode)
        if clsattr is not None:
            return clsattr().from_dict(dict_conf)

    @classmethod
    def from_bosminer(cls, toml_conf: dict):
        power_scaling = toml_conf.get("power_scaling")
        if power_scaling is None:
            power_scaling = toml_conf.get("performance_scaling")
        if power_scaling is not None:
            enabled = power_scaling.get("enabled")
            if enabled is not None:
                if enabled:
                    return cls.enabled().from_bosminer(power_scaling)
                else:
                    return cls.disabled()

        return cls.default()

    @classmethod
    def from_boser(cls, grpc_miner_conf: dict):
        try:
            dps_conf = grpc_miner_conf["dps"]
            if not dps_conf.get("enabled", False):
                return cls.disabled()
        except LookupError:
            return cls.default()

        conf = {"shutdown_enabled": PowerScalingShutdown.from_boser(dps_conf)}

        if dps_conf.get("minPowerTarget") is not None:
            conf["minimum_power"] = dps_conf["minPowerTarget"]["watt"]
        if dps_conf.get("powerStep") is not None:
            conf["power_step"] = dps_conf["powerStep"]["watt"]
        return cls.enabled(**conf)
