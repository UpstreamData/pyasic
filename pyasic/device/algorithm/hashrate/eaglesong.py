from __future__ import annotations

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.eaglesong import EaglesongUnit

from .unit import HashUnit


class EaglesongHashRate(AlgoHashRateType):
    rate: float
    unit: EaglesongUnit = HashUnit.EAGLESONG.default

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
