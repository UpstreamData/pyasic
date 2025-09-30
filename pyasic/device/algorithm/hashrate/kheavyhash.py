from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.kheavyhash import KHeavyHashUnit

from .unit import HashUnit


class KHeavyHashHashRate(AlgoHashRateType):
    rate: float
    unit: KHeavyHashUnit = HashUnit.KHEAVYHASH.default

    def into(self, other: KHeavyHashUnit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
