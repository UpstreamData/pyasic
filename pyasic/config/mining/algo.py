from __future__ import annotations

from dataclasses import dataclass, field

from pyasic.config.base import MinerConfigOption, MinerConfigValue


@dataclass
class StandardTuneAlgo(MinerConfigValue):
    mode: str = field(init=False, default="standard")

    def as_epic(self) -> str:
        return VOptAlgo().as_epic()


@dataclass
class VOptAlgo(MinerConfigValue):
    mode: str = field(init=False, default="voltage_optimizer")

    def as_epic(self) -> str:
        return "VoltageOptimizer"


@dataclass
class BoardTuneAlgo(MinerConfigValue):
    mode: str = field(init=False, default="board_tune")

    def as_epic(self) -> str:
        return "BoardTune"


@dataclass
class ChipTuneAlgo(MinerConfigValue):
    mode: str = field(init=False, default="chip_tune")

    def as_epic(self) -> str:
        return "ChipTune"


@dataclass
class TunerAlgo(MinerConfigOption):
    standard = StandardTuneAlgo
    voltage_optimizer = VOptAlgo
    board_tune = BoardTuneAlgo
    chip_tune = ChipTuneAlgo

    @classmethod
    def default(cls):
        return cls.standard()

    @classmethod
    def from_dict(cls, dict_conf: dict | None):
        mode = dict_conf.get("mode")
        if mode is None:
            return cls.default()

        cls_attr = getattr(cls, mode)
        if cls_attr is not None:
            return cls_attr().from_dict(dict_conf)
