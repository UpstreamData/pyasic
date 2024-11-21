from __future__ import annotations

from pyasic.data.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm import MinerAlgo
from pyasic.device.algorithm.equihash import EquihashUnit


class EquihashHashRate(AlgoHashRateType):
    rate: float
    unit: EquihashUnit = MinerAlgo.ETHASH.unit.default

    def __float__(self):
        return float(self.rate)

    def __int__(self):
        return int(self.rate)

    def __repr__(self):
        return f"{self.rate} {str(self.unit)}"

    def __round__(self, n: int = None):
        return round(self.rate, n)

    def __add__(self, other: EquihashHashRate | int | float) -> EquihashHashRate:
        if isinstance(other, EquihashHashRate):
            return EquihashHashRate(
                rate=self.rate + other.into(self.unit).rate, unit=self.unit
            )
        return EquihashHashRate(rate=self.rate + other, unit=self.unit)

    def __sub__(self, other: EquihashHashRate | int | float) -> EquihashHashRate:
        if isinstance(other, EquihashHashRate):
            return EquihashHashRate(
                rate=self.rate - other.into(self.unit).rate, unit=self.unit
            )
        return EquihashHashRate(rate=self.rate - other, unit=self.unit)

    def __truediv__(self, other: EquihashHashRate | int | float):
        if isinstance(other, EquihashHashRate):
            return EquihashHashRate(
                rate=self.rate / other.into(self.unit).rate, unit=self.unit
            )
        return EquihashHashRate(rate=self.rate / other, unit=self.unit)

    def __floordiv__(self, other: EquihashHashRate | int | float):
        if isinstance(other, EquihashHashRate):
            return EquihashHashRate(
                rate=self.rate // other.into(self.unit).rate, unit=self.unit
            )
        return EquihashHashRate(rate=self.rate // other, unit=self.unit)

    def __mul__(self, other: EquihashHashRate | int | float):
        if isinstance(other, EquihashHashRate):
            return EquihashHashRate(
                rate=self.rate * other.into(self.unit).rate, unit=self.unit
            )
        return EquihashHashRate(rate=self.rate * other, unit=self.unit)

    def into(self, other: EquihashUnit) -> EquihashHashRate:
        return EquihashHashRate(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
