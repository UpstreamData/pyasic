from __future__ import annotations

from pyasic.data.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm import MinerAlgo
from pyasic.device.algorithm.sha256 import SHA256Unit


class SHA256HashRate(AlgoHashRateType):
    rate: float
    unit: SHA256Unit = MinerAlgo.SHA256.unit.default

    def __float__(self):
        return float(self.rate)

    def __int__(self):
        return int(self.rate)

    def __repr__(self):
        return f"{self.rate} {str(self.unit)}"

    def __round__(self, n: int = None):
        return round(self.rate, n)

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
