from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.x11 import X11Unit

from .unit import HashUnit


class X11HashRate(AlgoHashRateType):
    rate: float
    unit: X11Unit = HashUnit.X11.default

    def into(self, other: X11Unit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
