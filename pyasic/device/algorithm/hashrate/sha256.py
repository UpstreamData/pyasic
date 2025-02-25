from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.sha256 import SHA256Unit

from .unit import HashUnit


class SHA256HashRate(AlgoHashRateType):
    rate: float
    unit: SHA256Unit = HashUnit.SHA256.default

    def into(self, other: SHA256Unit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
