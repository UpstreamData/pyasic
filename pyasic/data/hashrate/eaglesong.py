from __future__ import annotations

from pyasic.data.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm import MinerAlgo
from pyasic.device.algorithm.eaglesong import EaglesongUnit


class EaglesongHashRate(AlgoHashRateType):
    rate: float
    unit: EaglesongUnit = MinerAlgo.EAGLESONG.unit.default

    def __float__(self):
        return float(self.rate)

    def __int__(self):
        return int(self.rate)

    def __repr__(self):
        return f"{self.rate} {str(self.unit)}"

    def __round__(self, n: int = None):
        return round(self.rate, n)

    def __add__(self, other: EaglesongHashRate | int | float) -> EaglesongHashRate:
        if isinstance(other, EaglesongHashRate):
            return EaglesongHashRate(
                rate=self.rate + other.into(self.unit).rate, unit=self.unit
            )
        return EaglesongHashRate(rate=self.rate + other, unit=self.unit)

    def __sub__(self, other: EaglesongHashRate | int | float) -> EaglesongHashRate:
        if isinstance(other, EaglesongHashRate):
            return EaglesongHashRate(
                rate=self.rate - other.into(self.unit).rate, unit=self.unit
            )
        return EaglesongHashRate(rate=self.rate - other, unit=self.unit)

    def __truediv__(self, other: EaglesongHashRate | int | float):
        if isinstance(other, EaglesongHashRate):
            return EaglesongHashRate(
                rate=self.rate / other.into(self.unit).rate, unit=self.unit
            )
        return EaglesongHashRate(rate=self.rate / other, unit=self.unit)

    def __floordiv__(self, other: EaglesongHashRate | int | float):
        if isinstance(other, EaglesongHashRate):
            return EaglesongHashRate(
                rate=self.rate // other.into(self.unit).rate, unit=self.unit
            )
        return EaglesongHashRate(rate=self.rate // other, unit=self.unit)

    def __mul__(self, other: EaglesongHashRate | int | float):
        if isinstance(other, EaglesongHashRate):
            return EaglesongHashRate(
                rate=self.rate * other.into(self.unit).rate, unit=self.unit
            )
        return EaglesongHashRate(rate=self.rate * other, unit=self.unit)

    def into(self, other: EaglesongUnit) -> EaglesongHashRate:
        return EaglesongHashRate(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
