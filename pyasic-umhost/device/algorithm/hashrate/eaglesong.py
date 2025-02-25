from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.eaglesong import EaglesongUnit

from .unit import HashUnit


class EaglesongHashRate(AlgoHashRateType):
    rate: float
    unit: EaglesongUnit = HashUnit.EAGLESONG.default

    def into(self, other: EaglesongUnit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
