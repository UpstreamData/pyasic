from __future__ import annotations

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.blake256 import Blake256Unit

from .unit import HashUnit


class Blake256HashRate(AlgoHashRateType):
    rate: float
    unit: Blake256Unit = HashUnit.BLAKE256.default

    def __add__(self, other: Blake256HashRate | int | float) -> Blake256HashRate:
        if isinstance(other, Blake256HashRate):
            return Blake256HashRate(
                rate=self.rate + other.into(self.unit).rate, unit=self.unit
            )
        return Blake256HashRate(rate=self.rate + other, unit=self.unit)

    def __sub__(self, other: Blake256HashRate | int | float) -> Blake256HashRate:
        if isinstance(other, Blake256HashRate):
            return Blake256HashRate(
                rate=self.rate - other.into(self.unit).rate, unit=self.unit
            )
        return Blake256HashRate(rate=self.rate - other, unit=self.unit)

    def __truediv__(self, other: Blake256HashRate | int | float):
        if isinstance(other, Blake256HashRate):
            return Blake256HashRate(
                rate=self.rate / other.into(self.unit).rate, unit=self.unit
            )
        return Blake256HashRate(rate=self.rate / other, unit=self.unit)

    def __floordiv__(self, other: Blake256HashRate | int | float):
        if isinstance(other, Blake256HashRate):
            return Blake256HashRate(
                rate=self.rate // other.into(self.unit).rate, unit=self.unit
            )
        return Blake256HashRate(rate=self.rate // other, unit=self.unit)

    def __mul__(self, other: Blake256HashRate | int | float):
        if isinstance(other, Blake256HashRate):
            return Blake256HashRate(
                rate=self.rate * other.into(self.unit).rate, unit=self.unit
            )
        return Blake256HashRate(rate=self.rate * other, unit=self.unit)

    def into(self, other: Blake256Unit) -> Blake256HashRate:
        return Blake256HashRate(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
