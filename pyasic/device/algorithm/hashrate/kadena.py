from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.kadena import KadenaUnit

from .unit import HashUnit


class KadenaHashRate(AlgoHashRateType):
    rate: float
    unit: KadenaUnit = HashUnit.KADENA.default

    def into(self, other: KadenaUnit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
