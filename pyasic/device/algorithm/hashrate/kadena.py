from __future__ import annotations

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.kadena import KadenaUnit

from .unit import HashUnit


class KadenaHashRate(AlgoHashRateType):
    rate: float
    unit: KadenaUnit = HashUnit.KADENA.default

    def __add__(self, other: KadenaHashRate | int | float) -> KadenaHashRate:
        if isinstance(other, KadenaHashRate):
            return KadenaHashRate(
                rate=self.rate + other.into(self.unit).rate, unit=self.unit
            )
        return KadenaHashRate(rate=self.rate + other, unit=self.unit)

    def __sub__(self, other: KadenaHashRate | int | float) -> KadenaHashRate:
        if isinstance(other, KadenaHashRate):
            return KadenaHashRate(
                rate=self.rate - other.into(self.unit).rate, unit=self.unit
            )
        return KadenaHashRate(rate=self.rate - other, unit=self.unit)

    def __truediv__(self, other: KadenaHashRate | int | float):
        if isinstance(other, KadenaHashRate):
            return KadenaHashRate(
                rate=self.rate / other.into(self.unit).rate, unit=self.unit
            )
        return KadenaHashRate(rate=self.rate / other, unit=self.unit)

    def __floordiv__(self, other: KadenaHashRate | int | float):
        if isinstance(other, KadenaHashRate):
            return KadenaHashRate(
                rate=self.rate // other.into(self.unit).rate, unit=self.unit
            )
        return KadenaHashRate(rate=self.rate // other, unit=self.unit)

    def __mul__(self, other: KadenaHashRate | int | float):
        if isinstance(other, KadenaHashRate):
            return KadenaHashRate(
                rate=self.rate * other.into(self.unit).rate, unit=self.unit
            )
        return KadenaHashRate(rate=self.rate * other, unit=self.unit)

    def into(self, other: KadenaUnit) -> KadenaHashRate:
        return KadenaHashRate(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
