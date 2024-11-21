from __future__ import annotations

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.scrypt import ScryptUnit

from .unit import HashUnit


class ScryptHashRate(AlgoHashRateType):
    rate: float
    unit: ScryptUnit = HashUnit.SCRYPT.default

    def __add__(self, other: ScryptHashRate | int | float) -> ScryptHashRate:
        if isinstance(other, ScryptHashRate):
            return ScryptHashRate(
                rate=self.rate + other.into(self.unit).rate, unit=self.unit
            )
        return ScryptHashRate(rate=self.rate + other, unit=self.unit)

    def __sub__(self, other: ScryptHashRate | int | float) -> ScryptHashRate:
        if isinstance(other, ScryptHashRate):
            return ScryptHashRate(
                rate=self.rate - other.into(self.unit).rate, unit=self.unit
            )
        return ScryptHashRate(rate=self.rate - other, unit=self.unit)

    def __truediv__(self, other: ScryptHashRate | int | float):
        if isinstance(other, ScryptHashRate):
            return ScryptHashRate(
                rate=self.rate / other.into(self.unit).rate, unit=self.unit
            )
        return ScryptHashRate(rate=self.rate / other, unit=self.unit)

    def __floordiv__(self, other: ScryptHashRate | int | float):
        if isinstance(other, ScryptHashRate):
            return ScryptHashRate(
                rate=self.rate // other.into(self.unit).rate, unit=self.unit
            )
        return ScryptHashRate(rate=self.rate // other, unit=self.unit)

    def __mul__(self, other: ScryptHashRate | int | float):
        if isinstance(other, ScryptHashRate):
            return ScryptHashRate(
                rate=self.rate * other.into(self.unit).rate, unit=self.unit
            )
        return ScryptHashRate(rate=self.rate * other, unit=self.unit)

    def into(self, other: ScryptUnit) -> ScryptHashRate:
        return ScryptHashRate(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
