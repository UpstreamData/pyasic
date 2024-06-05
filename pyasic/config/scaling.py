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
    DpsHashrateTarget,
    DpsPowerTarget,
    DpsTarget,
    Power,
    SetDpsRequest,
    TeraHashrate,
)


@dataclass
class ScalingShutdownEnabled(MinerConfigValue):
    mode: str = field(init=False, default="enabled")
    duration: int = None

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "ScalingShutdownEnabled":
        return cls(duration=dict_conf.get("duration"))

    def as_bosminer(self) -> dict:
        cfg = {"shutdown_enabled": True}

        if self.duration is not None:
            cfg["shutdown_duration"] = self.duration

        return cfg

    def as_boser(self) -> dict:
        return {"enable_shutdown": True, "shutdown_duration": self.duration}


@dataclass
class ScalingShutdownDisabled(MinerConfigValue):
    mode: str = field(init=False, default="disabled")

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "ScalingShutdownDisabled":
        return cls()

    def as_bosminer(self) -> dict:
        return {"shutdown_enabled": False}

    def as_boser(self) -> dict:
        return {"enable_shutdown ": False}


class ScalingShutdown(MinerConfigOption):
    enabled = ScalingShutdownEnabled
    disabled = ScalingShutdownDisabled

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
class PowerScaling(MinerConfigValue):
    mode: str = field(init=False, default="power")
    step: int = None
    minimum: int = None
    shutdown: ScalingShutdownEnabled | ScalingShutdownDisabled = None

    @classmethod
    def from_bosminer(cls, power_scaling_conf: dict) -> "PowerScaling":
        power_step = power_scaling_conf.get("power_step")
        min_power = power_scaling_conf.get("min_psu_power_limit")
        if min_power is None:
            min_power = power_scaling_conf.get("min_power_target")
        sd_mode = ScalingShutdown.from_bosminer(power_scaling_conf)

        return cls(step=power_step, minimum=min_power, shutdown=sd_mode)

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "PowerScaling":
        cls_conf = {
            "step": dict_conf.get("step"),
            "minimum": dict_conf.get("minimum"),
        }
        shutdown = dict_conf.get("shutdown")
        if shutdown is not None:
            cls_conf["shutdown"] = ScalingShutdown.from_dict(shutdown)
        return cls(**cls_conf)

    def as_bosminer(self) -> dict:
        cfg = {"enabled": True}
        if self.step is not None:
            cfg["power_step"] = self.step
        if self.minimum is not None:
            cfg["min_power_target"] = self.minimum

        if self.shutdown is not None:
            cfg = {**cfg, **self.shutdown.as_bosminer()}

        return {"performance_scaling": cfg}

    def as_boser(self) -> dict:
        return {
            "set_dps": SetDpsRequest(
                enable=True,
                **self.shutdown.as_boser(),
                target=DpsTarget(
                    power_target=DpsPowerTarget(
                        power_step=Power(self.step),
                        min_power_target=Power(self.minimum),
                    )
                ),
            ),
        }


@dataclass
class HashrateScaling(MinerConfigValue):
    mode: str = field(init=False, default="hashrate")
    target: int = None
    step: int = None
    minimum: int = None
    algo: str = None
    shutdown: ScalingShutdownEnabled | ScalingShutdownDisabled = None

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "HashrateScaling":
        cls_conf = {
            "step": dict_conf.get("step"),
            "minimum": dict_conf.get("minimum"),
        }
        shutdown = dict_conf.get("shutdown")
        if shutdown is not None:
            cls_conf["shutdown"] = ScalingShutdown.from_dict(shutdown)
        return cls(**cls_conf)

    def as_boser(self) -> dict:
        return {
            "set_dps": SetDpsRequest(
                enable=True,
                **self.shutdown.as_boser(),
                target=DpsTarget(
                    hashrate_target=DpsHashrateTarget(
                        hashrate_step=TeraHashrate(self.step),
                        min_hashrate_target=TeraHashrate(self.minimum),
                    )
                ),
            ),
        }

    def as_epic(self) -> dict:
        mode = {
            "ptune": {
                "algo": self.algo,
                "target": self.target,
            }
        }
        if self.minimum is not None:
            mode["ptune"]["min_throttle"] = self.minimum
        if self.step is not None:
            mode["ptune"]["throttle_step"] = self.step
        return mode


@dataclass
class ScalingDisabled(MinerConfigValue):
    mode: str = field(init=False, default="disabled")


class ScalingConfig(MinerConfigOption):
    power = PowerScaling
    hashrate = HashrateScaling
    disabled = ScalingDisabled

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
                    return cls.power().from_bosminer(power_scaling)
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

        conf = {"shutdown_enabled": ScalingShutdown.from_boser(dps_conf)}

        if dps_conf.get("minPowerTarget") is not None:
            conf["minimum_power"] = dps_conf["minPowerTarget"]["watt"]
        if dps_conf.get("powerStep") is not None:
            conf["power_step"] = dps_conf["powerStep"]["watt"]
        return cls.power(**conf)

    @classmethod
    def from_epic(cls, web_conf: dict):
        # print(web_summary)
        try:
            tuner_running = web_conf["PerpetualTune"]["Running"]
            if not tuner_running:
                return cls.disabled()
            else:
                algo_info = web_conf["PerpetualTune"]["Algorithm"]
                if algo_info.get("VoltageOptimizer") is not None:
                    return cls.hashrate(
                        algo="VoltageOptimizer",
                        target=algo_info["VoltageOptimizer"].get("Target"),
                        minimum=algo_info["VoltageOptimizer"].get(
                            "Min Throttle Target"
                        ),
                        step=algo_info["VoltageOptimizer"].get("Throttle Step"),
                    )
                if algo_info.get("BoardTune") is not None:
                    return cls.hashrate(
                        algo="BoardTune",
                        target=algo_info["VoltageOptimizer"].get("Target"),
                        minimum=algo_info["VoltageOptimizer"].get(
                            "Min Throttle Target"
                        ),
                        step=algo_info["VoltageOptimizer"].get("Throttle Step"),
                    )
                # ChipTune does not have scaling, but will be added
                if algo_info.get("ChipTune") is not None:
                    return cls.hashrate(
                        algo="ChipTune",
                        target=algo_info["VoltageOptimizer"].get("Target"),
                    )
        except LookupError:
            return cls.default()
