from __future__ import annotations

from pyasic.data.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm import MinerAlgo
from pyasic.device.algorithm.blake256 import Blake256Unit


class Blake256HashRate(AlgoHashRateType):
    rate: float
    unit: Blake256Unit = MinerAlgo.BLAKE256.unit.default

    def __float__(self):
        return float(self.rate)

    def __int__(self):
        return int(self.rate)

    def __repr__(self):
        return f"{self.rate} {str(self.unit)}"

    def __round__(self, n: int = None):
        return round(self.rate, n)

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
