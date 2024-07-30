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

from pyasic import settings
from pyasic.config.base import MinerConfigOption, MinerConfigValue
from pyasic.web.braiins_os.proto.braiins.bos.v1 import (
    DpsHashrateTarget,
    DpsPowerTarget,
    DpsTarget,
    HashrateTargetMode,
    PerformanceMode,
    Power,
    PowerTargetMode,
    SaveAction,
    SetDpsRequest,
    SetPerformanceModeRequest,
    TeraHashrate,
    TunerPerformanceMode,
)

from .algo import TunerAlgo
from .scaling import ScalingConfig


@dataclass
class MiningModeNormal(MinerConfigValue):
    mode: str = field(init=False, default="normal")

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "MiningModeNormal":
        return cls()

    def as_am_modern(self) -> dict:
        if settings.get("antminer_mining_mode_as_str", False):
            return {"miner-mode": "0"}
        return {"miner-mode": 0}

    def as_wm(self) -> dict:
        return {"mode": self.mode}

    def as_auradine(self) -> dict:
        return {"mode": {"mode": self.mode}}

    def as_epic(self) -> dict:
        return {"ptune": {"enabled": False}}

    def as_goldshell(self) -> dict:
        return {"settings": {"level": 0}}

    def as_mara(self) -> dict:
        return {
            "mode": {
                "work-mode-selector": "Stock",
            }
        }


@dataclass
class MiningModeSleep(MinerConfigValue):
    mode: str = field(init=False, default="sleep")

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "MiningModeSleep":
        return cls()

    def as_am_modern(self) -> dict:
        if settings.get("antminer_mining_mode_as_str", False):
            return {"miner-mode": "1"}
        return {"miner-mode": 1}

    def as_wm(self) -> dict:
        return {"mode": self.mode}

    def as_auradine(self) -> dict:
        return {"mode": {"sleep": "on"}}

    def as_epic(self) -> dict:
        return {"ptune": {"algo": "Sleep", "target": 0}}

    def as_goldshell(self) -> dict:
        return {"settings": {"level": 3}}

    def as_mara(self) -> dict:
        return {
            "mode": {
                "work-mode-selector": "Sleep",
            }
        }


@dataclass
class MiningModeLPM(MinerConfigValue):
    mode: str = field(init=False, default="low")

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "MiningModeLPM":
        return cls()

    def as_am_modern(self) -> dict:
        if settings.get("antminer_mining_mode_as_str", False):
            return {"miner-mode": "3"}
        return {"miner-mode": 3}

    def as_wm(self) -> dict:
        return {"mode": self.mode}

    def as_auradine(self) -> dict:
        return {"mode": {"mode": "eco"}}

    def as_goldshell(self) -> dict:
        return {"settings": {"level": 1}}


@dataclass
class MiningModeHPM(MinerConfigValue):
    mode: str = field(init=False, default="high")

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "MiningModeHPM":
        return cls()

    def as_am_modern(self) -> dict:
        if settings.get("antminer_mining_mode_as_str", False):
            return {"miner-mode": "0"}
        return {"miner-mode": 0}

    def as_wm(self) -> dict:
        return {"mode": self.mode}

    def as_auradine(self) -> dict:
        return {"mode": {"mode": "turbo"}}


@dataclass
class MiningModePowerTune(MinerConfigValue):
    mode: str = field(init=False, default="power_tuning")
    power: int = None
    algo: TunerAlgo = field(default_factory=TunerAlgo.default)
    scaling: ScalingConfig = None

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "MiningModePowerTune":
        cls_conf = {}
        if dict_conf.get("power"):
            cls_conf["power"] = dict_conf["power"]
        if dict_conf.get("algo"):
            cls_conf["algo"] = TunerAlgo.from_dict(dict_conf["algo"])
        if dict_conf.get("scaling"):
            cls_conf["scaling"] = ScalingConfig.from_dict(dict_conf["scaling"])

        return cls(**cls_conf)

    def as_am_modern(self) -> dict:
        if settings.get("antminer_mining_mode_as_str", False):
            return {"miner-mode": "0"}
        return {"miner-mode": 0}

    def as_wm(self) -> dict:
        if self.power is not None:
            return {"mode": self.mode, self.mode: {"wattage": self.power}}
        return {}

    def as_bosminer(self) -> dict:
        tuning_cfg = {"enabled": True, "mode": "power_target"}
        if self.power is not None:
            tuning_cfg["power_target"] = self.power

        cfg = {"autotuning": tuning_cfg}

        if self.scaling is not None:
            scaling_cfg = {"enabled": True}
            if self.scaling.step is not None:
                scaling_cfg["power_step"] = self.scaling.step
            if self.scaling.minimum is not None:
                scaling_cfg["min_power_target"] = self.scaling.minimum
            if self.scaling.shutdown is not None:
                scaling_cfg = {**scaling_cfg, **self.scaling.shutdown.as_bosminer()}
            cfg["performance_scaling"] = scaling_cfg

        return cfg

    def as_boser(self) -> dict:
        cfg = {
            "set_performance_mode": SetPerformanceModeRequest(
                save_action=SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
                mode=PerformanceMode(
                    tuner_mode=TunerPerformanceMode(
                        power_target=PowerTargetMode(
                            power_target=Power(watt=self.power)
                        )
                    )
                ),
            ),
        }
        if self.scaling is not None:
            sd_cfg = {}
            if self.scaling.shutdown is not None:
                sd_cfg = self.scaling.shutdown.as_boser()
            cfg["set_dps"] = (
                SetDpsRequest(
                    enable=True,
                    **sd_cfg,
                    target=DpsTarget(
                        power_target=DpsPowerTarget(
                            power_step=Power(self.scaling.step),
                            min_power_target=Power(self.scaling.minimum),
                        )
                    ),
                ),
            )
        return cfg

    def as_auradine(self) -> dict:
        return {"mode": {"mode": "custom", "tune": "power", "power": self.power}}

    def as_mara(self) -> dict:
        return {
            "mode": {
                "work-mode-selector": "Auto",
                "concorde": {
                    "mode-select": "PowerTarget",
                    "power-target": self.power,
                },
            }
        }


@dataclass
class MiningModeHashrateTune(MinerConfigValue):
    mode: str = field(init=False, default="hashrate_tuning")
    hashrate: int = None
    algo: TunerAlgo = field(default_factory=TunerAlgo.default)
    scaling: ScalingConfig = None

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "MiningModeHashrateTune":
        cls_conf = {}
        if dict_conf.get("hashrate"):
            cls_conf["hashrate"] = dict_conf["hashrate"]
        if dict_conf.get("algo"):
            cls_conf["algo"] = TunerAlgo.from_dict(dict_conf["algo"])
        if dict_conf.get("scaling"):
            cls_conf["scaling"] = ScalingConfig.from_dict(dict_conf["scaling"])

        return cls(**cls_conf)

    def as_am_modern(self) -> dict:
        if settings.get("antminer_mining_mode_as_str", False):
            return {"miner-mode": "0"}
        return {"miner-mode": 0}

    def as_bosminer(self) -> dict:
        conf = {"enabled": True, "mode": "hashrate_target"}
        if self.hashrate is not None:
            conf["hashrate_target"] = self.hashrate
        return {"autotuning": conf}

    @property
    def as_boser(self) -> dict:
        cfg = {
            "set_performance_mode": SetPerformanceModeRequest(
                save_action=SaveAction.SAVE_ACTION_SAVE_AND_APPLY,
                mode=PerformanceMode(
                    tuner_mode=TunerPerformanceMode(
                        hashrate_target=HashrateTargetMode(
                            hashrate_target=TeraHashrate(
                                terahash_per_second=self.hashrate
                            )
                        )
                    )
                ),
            )
        }
        if self.scaling is not None:
            sd_cfg = {}
            if self.scaling.shutdown is not None:
                sd_cfg = self.scaling.shutdown.as_boser()
            cfg["set_dps"] = (
                SetDpsRequest(
                    enable=True,
                    **sd_cfg,
                    target=DpsTarget(
                        hashrate_target=DpsHashrateTarget(
                            hashrate_step=TeraHashrate(self.scaling.step),
                            min_hashrate_target=TeraHashrate(self.scaling.minimum),
                        )
                    ),
                ),
            )
        return cfg

    def as_auradine(self) -> dict:
        return {"mode": {"mode": "custom", "tune": "ths", "ths": self.hashrate}}

    def as_epic(self) -> dict:
        mode = {
            "ptune": {
                "algo": self.algo.as_epic(),
                "target": self.hashrate,
            }
        }
        if self.scaling is not None:
            if self.scaling.minimum is not None:
                mode["ptune"]["min_throttle"] = self.scaling.minimum
            if self.scaling.step is not None:
                mode["ptune"]["throttle_step"] = self.scaling.step
        return mode

    def as_mara(self) -> dict:
        return {
            "mode": {
                "work-mode-selector": "Auto",
                "concorde": {
                    "mode-select": "Hashrate",
                    "hash-target": self.hashrate,
                },
            }
        }


@dataclass
class ManualBoardSettings(MinerConfigValue):
    freq: float
    volt: float

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "ManualBoardSettings":
        return cls(freq=dict_conf["freq"], volt=dict_conf["volt"])

    def as_am_modern(self) -> dict:
        if settings.get("antminer_mining_mode_as_str", False):
            return {"miner-mode": "0"}
        return {"miner-mode": 0}


@dataclass
class MiningModeManual(MinerConfigValue):
    mode: str = field(init=False, default="manual")

    global_freq: float
    global_volt: float
    boards: dict[int, ManualBoardSettings] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> "MiningModeManual":
        return cls(
            global_freq=dict_conf["global_freq"],
            global_volt=dict_conf["global_volt"],
            boards={i: ManualBoardSettings.from_dict(dict_conf[i]) for i in dict_conf},
        )

    def as_am_modern(self) -> dict:
        if settings.get("antminer_mining_mode_as_str", False):
            return {"miner-mode": "0"}
        return {"miner-mode": 0}

    @classmethod
    def from_vnish(cls, web_overclock_settings: dict) -> "MiningModeManual":
        # will raise KeyError if it cant find the settings, values cannot be empty
        voltage = web_overclock_settings["globals"]["volt"]
        freq = web_overclock_settings["globals"]["freq"]
        boards = {
            idx: ManualBoardSettings(
                freq=board["freq"],
                volt=voltage if not board["freq"] == 0 else 0,
            )
            for idx, board in enumerate(web_overclock_settings["chains"])
        }
        return cls(global_freq=freq, global_volt=voltage, boards=boards)

    @classmethod
    def from_epic(cls, epic_conf: dict) -> "MiningModeManual":
        voltage = 0
        freq = 0
        if epic_conf.get("HwConfig") is not None:
            freq = epic_conf["HwConfig"]["Boards Target Clock"][0]["Data"]
        if epic_conf.get("Power Supply Stats") is not None:
            voltage = epic_conf["Power Supply Stats"]["Target Voltage"]
        boards = {}
        if epic_conf.get("HBs") is not None:
            boards = {
                board["Index"]: ManualBoardSettings(
                    freq=board["Core Clock Avg"], volt=board["Input Voltage"]
                )
                for board in epic_conf["HBs"]
            }
        return cls(global_freq=freq, global_volt=voltage, boards=boards)

    def as_mara(self) -> dict:
        return {
            "mode": {
                "work-mode-selector": "Fixed",
                "fixed": {
                    "frequency": str(self.global_freq),
                    "voltage": self.global_volt,
                },
            }
        }


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
            tuner_running = web_conf["PerpetualTune"]["Running"]
            if tuner_running:
                algo_info = web_conf["PerpetualTune"]["Algorithm"]
                if algo_info.get("VoltageOptimizer") is not None:
                    scaling_cfg = None
                    if "Throttle Step" in algo_info["VoltageOptimizer"]:
                        scaling_cfg = ScalingConfig(
                            minimum=algo_info["VoltageOptimizer"].get(
                                "Min Throttle Target"
                            ),
                            step=algo_info["VoltageOptimizer"].get("Throttle Step"),
                        )

                    return cls.hashrate_tuning(
                        hashrate=algo_info["VoltageOptimizer"].get("Target"),
                        algo=TunerAlgo.voltage_optimizer(),
                        scaling=scaling_cfg,
                    )
                elif algo_info.get("BoardTune") is not None:
                    scaling_cfg = None
                    if "Throttle Step" in algo_info["BoardTune"]:
                        scaling_cfg = ScalingConfig(
                            minimum=algo_info["BoardTune"].get("Min Throttle Target"),
                            step=algo_info["BoardTune"].get("Throttle Step"),
                        )

                    return cls.hashrate_tuning(
                        hashrate=algo_info["BoardTune"].get("Target"),
                        algo=TunerAlgo.board_tune(),
                        scaling=scaling_cfg,
                    )
                else:
                    return cls.hashrate_tuning(
                        hashrate=algo_info["ChipTune"].get("Target"),
                        algo=TunerAlgo.chip_tune(),
                    )
            else:
                return MiningModeManual.from_epic(web_conf)
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
            return cls.power_tuning(
                autotuning_conf["psu_power_limit"],
                scaling=ScalingConfig.from_bosminer(toml_conf, mode="power"),
            )
        if autotuning_conf.get("mode") is not None:
            # new autotuning conf
            mode = autotuning_conf["mode"]
            if mode == "power_target":
                if autotuning_conf.get("power_target") is not None:
                    return cls.power_tuning(
                        autotuning_conf["power_target"],
                        scaling=ScalingConfig.from_bosminer(toml_conf, mode="power"),
                    )
                return cls.power_tuning(
                    scaling=ScalingConfig.from_bosminer(toml_conf, mode="power"),
                )
            if mode == "hashrate_target":
                if autotuning_conf.get("hashrate_target") is not None:
                    return cls.hashrate_tuning(
                        autotuning_conf["hashrate_target"],
                        scaling=ScalingConfig.from_bosminer(toml_conf, mode="hashrate"),
                    )
                return cls.hashrate_tuning(
                    scaling=ScalingConfig.from_bosminer(toml_conf, mode="hashrate"),
                )

    @classmethod
    def from_vnish(cls, web_settings: dict):
        try:
            mode_settings = web_settings["miner"]["overclock"]
        except KeyError:
            return cls.default()

        if mode_settings["preset"] == "disabled":
            return MiningModeManual.from_vnish(mode_settings)
        else:
            return cls.power_tuning(int(mode_settings["preset"]))

    @classmethod
    def from_boser(cls, grpc_miner_conf: dict):
        try:
            tuner_conf = grpc_miner_conf["tuner"]
            if not tuner_conf.get("enabled", False):
                return cls.default()
        except LookupError:
            return cls.default()

        if tuner_conf.get("tunerMode") is not None:
            if tuner_conf["tunerMode"] == 1:
                if tuner_conf.get("powerTarget") is not None:
                    return cls.power_tuning(
                        tuner_conf["powerTarget"]["watt"],
                        scaling=ScalingConfig.from_boser(grpc_miner_conf, mode="power"),
                    )
                return cls.power_tuning(
                    scaling=ScalingConfig.from_boser(grpc_miner_conf, mode="power")
                )

            if tuner_conf["tunerMode"] == 2:
                if tuner_conf.get("hashrateTarget") is not None:
                    return cls.hashrate_tuning(
                        int(tuner_conf["hashrateTarget"]["terahashPerSecond"]),
                        scaling=ScalingConfig.from_boser(
                            grpc_miner_conf, mode="hashrate"
                        ),
                    )
                return cls.hashrate_tuning(
                    scaling=ScalingConfig.from_boser(grpc_miner_conf, mode="hashrate"),
                )

        if tuner_conf.get("powerTarget") is not None:
            return cls.power_tuning(
                tuner_conf["powerTarget"]["watt"],
                scaling=ScalingConfig.from_boser(grpc_miner_conf, mode="power"),
            )

        if tuner_conf.get("hashrateTarget") is not None:
            return cls.hashrate_tuning(
                int(tuner_conf["hashrateTarget"]["terahashPerSecond"]),
                scaling=ScalingConfig.from_boser(grpc_miner_conf, mode="hashrate"),
            )

        return cls.default()

    @classmethod
    def from_auradine(cls, web_mode: dict):
        try:
            mode_data = web_mode["Mode"][0]
            if mode_data.get("Sleep") == "on":
                return cls.sleep()
            if mode_data.get("Mode") == "normal":
                return cls.normal()
            if mode_data.get("Mode") == "eco":
                return cls.low()
            if mode_data.get("Mode") == "turbo":
                return cls.high()
            if mode_data.get("Ths") is not None:
                return cls.hashrate_tuning(mode_data["Ths"])
            if mode_data.get("Power") is not None:
                return cls.power_tuning(mode_data["Power"])
        except LookupError:
            return cls.default()

    @classmethod
    def from_mara(cls, web_config: dict):
        try:
            mode = web_config["mode"]["work-mode-selector"]
            if mode == "Fixed":
                fixed_conf = web_config["mode"]["fixed"]
                return cls.manual(
                    global_freq=int(fixed_conf["frequency"]),
                    global_volt=fixed_conf["voltage"],
                )
            elif mode == "Stock":
                return cls.normal()
            elif mode == "Sleep":
                return cls.sleep()
            elif mode == "Auto":
                auto_conf = web_config["mode"]["concorde"]
                auto_mode = auto_conf["mode-select"]
                if auto_mode == "Hashrate":
                    return cls.hashrate_tuning(hashrate=auto_conf["hash-target"])
                elif auto_mode == "PowerTarget":
                    return cls.power_tuning(power=auto_conf["power-target"])
        except LookupError:
            pass
        return cls.default()
