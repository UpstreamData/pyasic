from __future__ import annotations

from dataclasses import field
from typing import Any

from pyasic.config.base import MinerConfigOption, MinerConfigValue


class StandardTuneAlgo(MinerConfigValue):
    mode: str = field(init=False, default="standard")

    def as_epic(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return VOptAlgo().as_epic(*args, **kwargs)


class VOptAlgo(MinerConfigValue):
    mode: str = field(init=False, default="voltage_optimizer")

    def as_epic(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"algorithm": "VoltageOptimizer"}


class BoardTuneAlgo(MinerConfigValue):
    mode: str = field(init=False, default="board_tune")

    def as_epic(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"algorithm": "BoardTune"}


class ChipTuneAlgo(MinerConfigValue):
    mode: str = field(init=False, default="chip_tune")

    def as_epic(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"algorithm": "ChipTune"}


# Type alias for all possible tuner algorithm instances
TunerAlgoInstance = StandardTuneAlgo | VOptAlgo | BoardTuneAlgo | ChipTuneAlgo


class TunerAlgo(MinerConfigOption):
    standard = StandardTuneAlgo
    voltage_optimizer = VOptAlgo
    board_tune = BoardTuneAlgo
    chip_tune = ChipTuneAlgo

    @classmethod
    def default(cls) -> TunerAlgo:
        return cls.standard

    @classmethod
    def from_dict(cls, dict_conf: dict[str, Any] | TunerAlgo | None) -> TunerAlgo:
        if dict_conf is None:
            return cls.default()

        if isinstance(dict_conf, cls):
            return dict_conf

        if not isinstance(dict_conf, dict):
            return cls.default()

        mode = dict_conf.get("mode")
        if mode is None:
            return cls.default()

        for member in cls:
            if member.name == mode:
                return member
        return cls.default()

    def as_dict(self) -> dict[str, Any]:
        algo_class = self.value
        if isinstance(algo_class, type) and issubclass(algo_class, MinerConfigValue):
            return algo_class().as_dict()
        return {}
