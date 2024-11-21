from __future__ import annotations

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.x11 import X11Unit

from .unit import HashUnit


class X11HashRate(AlgoHashRateType):
    rate: float
    unit: X11Unit = HashUnit.X11.default

    def __add__(self, other: X11HashRate | int | float) -> X11HashRate:
        if isinstance(other, X11HashRate):
            return X11HashRate(
                rate=self.rate + other.into(self.unit).rate, unit=self.unit
            )
        return X11HashRate(rate=self.rate + other, unit=self.unit)

    def __sub__(self, other: X11HashRate | int | float) -> X11HashRate:
        if isinstance(other, X11HashRate):
            return X11HashRate(
                rate=self.rate - other.into(self.unit).rate, unit=self.unit
            )
        return X11HashRate(rate=self.rate - other, unit=self.unit)

    def __truediv__(self, other: X11HashRate | int | float):
        if isinstance(other, X11HashRate):
            return X11HashRate(
                rate=self.rate / other.into(self.unit).rate, unit=self.unit
            )
        return X11HashRate(rate=self.rate / other, unit=self.unit)

    def __floordiv__(self, other: X11HashRate | int | float):
        if isinstance(other, X11HashRate):
            return X11HashRate(
                rate=self.rate // other.into(self.unit).rate, unit=self.unit
            )
        return X11HashRate(rate=self.rate // other, unit=self.unit)

    def __mul__(self, other: X11HashRate | int | float):
        if isinstance(other, X11HashRate):
            return X11HashRate(
                rate=self.rate * other.into(self.unit).rate, unit=self.unit
            )
        return X11HashRate(rate=self.rate * other, unit=self.unit)

    def into(self, other: X11Unit) -> X11HashRate:
        return X11HashRate(rate=self.rate / (other.value / self.unit.value), unit=other)
