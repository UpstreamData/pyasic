from __future__ import annotations

from pyasic.data.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm import MinerAlgo
from pyasic.device.algorithm.x11 import X11Unit


class X11HashRate(AlgoHashRateType):
    rate: float
    unit: X11Unit = MinerAlgo.X11.unit.default

    def __float__(self):
        return float(self.rate)

    def __int__(self):
        return int(self.rate)

    def __repr__(self):
        return f"{self.rate} {str(self.unit)}"

    def __round__(self, n: int = None):
        return round(self.rate, n)

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
