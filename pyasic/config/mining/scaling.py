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
class ScalingShutdown(MinerConfigValue):
    enabled: bool = False
    duration: int = None

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "ScalingShutdown":
        return cls(
            enabled=dict_conf.get("enabled", False), duration=dict_conf.get("duration")
        )

    @classmethod
    def from_bosminer(cls, power_scaling_conf: dict):
        sd_enabled = power_scaling_conf.get("shutdown_enabled")
        if sd_enabled is not None:
            return cls(sd_enabled, power_scaling_conf.get("shutdown_duration"))
        return None

    @classmethod
    def from_boser(cls, power_scaling_conf: dict):
        sd_enabled = power_scaling_conf.get("shutdownEnabled")
        if sd_enabled is not None:
            try:
                return cls(sd_enabled, power_scaling_conf["shutdownDuration"]["hours"])
            except KeyError:
                return cls(sd_enabled)
        return None

    def as_bosminer(self) -> dict:
        cfg = {"shutdown_enabled": self.enabled}

        if self.duration is not None:
            cfg["shutdown_duration"] = self.duration

        return cfg

    def as_boser(self) -> dict:
        return {"enable_shutdown": self.enabled, "shutdown_duration": self.duration}


@dataclass
class ScalingConfig(MinerConfigValue):
    step: int = None
    minimum: int = None
    shutdown: ScalingShutdown = None

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "ScalingConfig":
        cls_conf = {
            "step": dict_conf.get("step"),
            "minimum": dict_conf.get("minimum"),
        }
        shutdown = dict_conf.get("shutdown")
        if shutdown is not None:
            cls_conf["shutdown"] = ScalingShutdown.from_dict(shutdown)
        return cls(**cls_conf)

    @classmethod
    def from_bosminer(cls, toml_conf: dict, mode: str = None):
        if mode == "power":
            return cls._from_bosminer_power(toml_conf)
        if mode == "hashrate":
            # not implemented yet
            pass

    @classmethod
    def _from_bosminer_power(cls, toml_conf: dict):
        power_scaling = toml_conf.get("power_scaling")
        if power_scaling is None:
            power_scaling = toml_conf.get("performance_scaling")
        if power_scaling is not None:
            enabled = power_scaling.get("enabled")
            if not enabled:
                return None
            power_step = power_scaling.get("power_step")
            min_power = power_scaling.get("min_psu_power_limit")
            if min_power is None:
                min_power = power_scaling.get("min_power_target")
            sd_mode = ScalingShutdown.from_bosminer(power_scaling)

            return cls(step=power_step, minimum=min_power, shutdown=sd_mode)

    @classmethod
    def from_boser(cls, grpc_miner_conf: dict, mode: str = None):
        if mode == "power":
            return cls._from_boser_power(grpc_miner_conf)
        if mode == "hashrate":
            # not implemented yet
            pass

    @classmethod
    def _from_boser_power(cls, grpc_miner_conf: dict):
        try:
            dps_conf = grpc_miner_conf["dps"]
            if not dps_conf.get("enabled", False):
                return None
        except LookupError:
            return None

        conf = {"shutdown": ScalingShutdown.from_boser(dps_conf)}

        if dps_conf.get("minPowerTarget") is not None:
            conf["minimum"] = dps_conf["minPowerTarget"]["watt"]
        if dps_conf.get("powerStep") is not None:
            conf["step"] = dps_conf["powerStep"]["watt"]
        return cls(**conf)
