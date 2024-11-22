from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeVar, Union

from pyasic.config.base import MinerConfigOption, MinerConfigValue


class StandardTuneAlgo(MinerConfigValue):
    mode: str = field(init=False, default="standard")

    def as_epic(self) -> str:
        return VOptAlgo().as_epic()


class VOptAlgo(MinerConfigValue):
    mode: str = field(init=False, default="voltage_optimizer")

    def as_epic(self) -> str:
        return "VoltageOptimizer"


class BoardTuneAlgo(MinerConfigValue):
    mode: str = field(init=False, default="board_tune")

    def as_epic(self) -> str:
        return "BoardTune"


class ChipTuneAlgo(MinerConfigValue):
    mode: str = field(init=False, default="chip_tune")

    def as_epic(self) -> str:
        return "ChipTune"


class TunerAlgo(MinerConfigOption):
    standard = StandardTuneAlgo
    voltage_optimizer = VOptAlgo
    board_tune = BoardTuneAlgo
    chip_tune = ChipTuneAlgo

    @classmethod
    def default(cls) -> TunerAlgoType:
        return cls.standard()

    @classmethod
    def from_dict(cls, dict_conf: dict | None) -> TunerAlgoType:
        mode = dict_conf.get("mode")
        if mode is None:
            return cls.default()

        cls_attr = getattr(cls, mode)
        if cls_attr is not None:
            return cls_attr().from_dict(dict_conf)


TunerAlgoType = TypeVar(
    "TunerAlgoType",
    bound=Union[
        StandardTuneAlgo,
        VOptAlgo,
        BoardTuneAlgo,
        ChipTuneAlgo,
    ],
)
