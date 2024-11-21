from __future__ import annotations

from .hashrate.base import AlgoHashRateType
from .hashrate.unit.base import AlgoHashRateUnitType


class MinerAlgoType(str):
    hashrate: type[AlgoHashRateType]
    unit: type[AlgoHashRateUnitType]
