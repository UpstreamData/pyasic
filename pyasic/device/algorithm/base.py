from __future__ import annotations

from .hashrate.base import AlgoHashRateType
from .hashrate.unit.base import AlgoHashRateUnitType


class MinerAlgoMeta(type):
    name: str

    def __str__(cls):
        return cls.name


class MinerAlgoType(metaclass=MinerAlgoMeta):
    hashrate: type[AlgoHashRateType]
    unit: type[AlgoHashRateUnitType]
