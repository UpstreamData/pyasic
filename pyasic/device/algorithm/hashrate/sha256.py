from __future__ import annotations

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.sha256 import SHA256Unit

from .unit import HashUnit


class SHA256HashRate(AlgoHashRateType):
    rate: float
    unit: SHA256Unit = HashUnit.SHA256.default

    def __add__(self, other: SHA256HashRate | int | float) -> SHA256HashRate:
        if isinstance(other, SHA256HashRate):
            return SHA256HashRate(
                rate=self.rate + other.into(self.unit).rate, unit=self.unit
            )
        return SHA256HashRate(rate=self.rate + other, unit=self.unit)

    def __sub__(self, other: SHA256HashRate | int | float) -> SHA256HashRate:
        if isinstance(other, SHA256HashRate):
            return SHA256HashRate(
                rate=self.rate - other.into(self.unit).rate, unit=self.unit
            )
        return SHA256HashRate(rate=self.rate - other, unit=self.unit)

    def __truediv__(self, other: SHA256HashRate | int | float):
        if isinstance(other, SHA256HashRate):
            return SHA256HashRate(
                rate=self.rate / other.into(self.unit).rate, unit=self.unit
            )
        return SHA256HashRate(rate=self.rate / other, unit=self.unit)

    def __floordiv__(self, other: SHA256HashRate | int | float):
        if isinstance(other, SHA256HashRate):
            return SHA256HashRate(
                rate=self.rate // other.into(self.unit).rate, unit=self.unit
            )
        return SHA256HashRate(rate=self.rate // other, unit=self.unit)

    def __mul__(self, other: SHA256HashRate | int | float):
        if isinstance(other, SHA256HashRate):
            return SHA256HashRate(
                rate=self.rate * other.into(self.unit).rate, unit=self.unit
            )
        return SHA256HashRate(rate=self.rate * other, unit=self.unit)

    def into(self, other: SHA256Unit) -> SHA256HashRate:
        return SHA256HashRate(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
