from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.ethash import EtHashUnit

from .unit import HashUnit


class EtHashHashRate(AlgoHashRateType):
    rate: float
    unit: EtHashUnit = HashUnit.ETHASH.default

    def into(self, other: EtHashUnit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
