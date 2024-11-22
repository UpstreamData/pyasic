from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.equihash import EquihashUnit

from .unit import HashUnit


class EquihashHashRate(AlgoHashRateType):
    rate: float
    unit: EquihashUnit = HashUnit.ETHASH.default

    def into(self, other: EquihashUnit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
