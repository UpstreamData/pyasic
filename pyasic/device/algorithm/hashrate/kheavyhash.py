from __future__ import annotations

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.kheavyhash import KHeavyHashUnit

from .unit import HashUnit


class KHeavyHashHashRate(AlgoHashRateType):
    rate: float
    unit: KHeavyHashUnit = HashUnit.KHEAVYHASH.default

    def __add__(self, other: KHeavyHashHashRate | int | float) -> KHeavyHashHashRate:
        if isinstance(other, KHeavyHashHashRate):
            return KHeavyHashHashRate(
                rate=self.rate + other.into(self.unit).rate, unit=self.unit
            )
        return KHeavyHashHashRate(rate=self.rate + other, unit=self.unit)

    def __sub__(self, other: KHeavyHashHashRate | int | float) -> KHeavyHashHashRate:
        if isinstance(other, KHeavyHashHashRate):
            return KHeavyHashHashRate(
                rate=self.rate - other.into(self.unit).rate, unit=self.unit
            )
        return KHeavyHashHashRate(rate=self.rate - other, unit=self.unit)

    def __truediv__(self, other: KHeavyHashHashRate | int | float):
        if isinstance(other, KHeavyHashHashRate):
            return KHeavyHashHashRate(
                rate=self.rate / other.into(self.unit).rate, unit=self.unit
            )
        return KHeavyHashHashRate(rate=self.rate / other, unit=self.unit)

    def __floordiv__(self, other: KHeavyHashHashRate | int | float):
        if isinstance(other, KHeavyHashHashRate):
            return KHeavyHashHashRate(
                rate=self.rate // other.into(self.unit).rate, unit=self.unit
            )
        return KHeavyHashHashRate(rate=self.rate // other, unit=self.unit)

    def __mul__(self, other: KHeavyHashHashRate | int | float):
        if isinstance(other, KHeavyHashHashRate):
            return KHeavyHashHashRate(
                rate=self.rate * other.into(self.unit).rate, unit=self.unit
            )
        return KHeavyHashHashRate(rate=self.rate * other, unit=self.unit)

    def into(self, other: KHeavyHashUnit) -> KHeavyHashHashRate:
        return KHeavyHashHashRate(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
