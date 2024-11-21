from __future__ import annotations

from pyasic.data.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm import MinerAlgo
from pyasic.device.algorithm.ethash import EtHashUnit


class EtHashHashRate(AlgoHashRateType):
    rate: float
    unit: EtHashUnit = MinerAlgo.ETHASH.unit.default

    def __float__(self):
        return float(self.rate)

    def __int__(self):
        return int(self.rate)

    def __repr__(self):
        return f"{self.rate} {str(self.unit)}"

    def __round__(self, n: int = None):
        return round(self.rate, n)

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
