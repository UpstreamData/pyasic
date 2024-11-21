from __future__ import annotations

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.ethash import EtHashUnit

from .unit import HashUnit


class EtHashHashRate(AlgoHashRateType):
    rate: float
    unit: EtHashUnit = HashUnit.ETHASH.default

    def __add__(self, other: EtHashHashRate | int | float) -> EtHashHashRate:
        if isinstance(other, EtHashHashRate):
            return EtHashHashRate(
                rate=self.rate + other.into(self.unit).rate, unit=self.unit
            )
        return EtHashHashRate(rate=self.rate + other, unit=self.unit)

    def __sub__(self, other: EtHashHashRate | int | float) -> EtHashHashRate:
        if isinstance(other, EtHashHashRate):
            return EtHashHashRate(
                rate=self.rate - other.into(self.unit).rate, unit=self.unit
            )
        return EtHashHashRate(rate=self.rate - other, unit=self.unit)

    def __truediv__(self, other: EtHashHashRate | int | float):
        if isinstance(other, EtHashHashRate):
            return EtHashHashRate(
                rate=self.rate / other.into(self.unit).rate, unit=self.unit
            )
        return EtHashHashRate(rate=self.rate / other, unit=self.unit)

    def __floordiv__(self, other: EtHashHashRate | int | float):
        if isinstance(other, EtHashHashRate):
            return EtHashHashRate(
                rate=self.rate // other.into(self.unit).rate, unit=self.unit
            )
        return EtHashHashRate(rate=self.rate // other, unit=self.unit)

    def __mul__(self, other: EtHashHashRate | int | float):
        if isinstance(other, EtHashHashRate):
            return EtHashHashRate(
                rate=self.rate * other.into(self.unit).rate, unit=self.unit
            )
        return EtHashHashRate(rate=self.rate * other, unit=self.unit)

    def into(self, other: EtHashUnit) -> EtHashHashRate:
        return EtHashHashRate(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
