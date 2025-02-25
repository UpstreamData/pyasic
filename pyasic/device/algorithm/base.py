from __future__ import annotations

from .hashrate.base import AlgoHashRateType, GenericHashrate
from .hashrate.unit.base import AlgoHashRateUnitType, GenericUnit


class MinerAlgoMeta(type):
    name: str

    def __str__(cls):
        return cls.name


class MinerAlgoType(metaclass=MinerAlgoMeta):
    hashrate: type[AlgoHashRateType]
    unit: type[AlgoHashRateUnitType]


class GenericAlgo(MinerAlgoType):
    hashrate: type[GenericHashrate] = GenericHashrate
    unit: type[GenericUnit] = GenericUnit

    name = "Generic (Unknown)"
