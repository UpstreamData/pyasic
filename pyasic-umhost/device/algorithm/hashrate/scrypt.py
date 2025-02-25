from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.scrypt import ScryptUnit

from .unit import HashUnit


class ScryptHashRate(AlgoHashRateType):
    rate: float
    unit: ScryptUnit = HashUnit.SCRYPT.default

    def into(self, other: ScryptUnit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
