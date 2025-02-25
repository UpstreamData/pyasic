from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.blake256 import Blake256Unit

from .unit import HashUnit


class Blake256HashRate(AlgoHashRateType):
    rate: float
    unit: Blake256Unit = HashUnit.BLAKE256.default

    def into(self, other: Blake256Unit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
