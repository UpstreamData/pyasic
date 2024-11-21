from __future__ import annotations

from pyasic.data.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm import MinerAlgo
from pyasic.device.algorithm.handshake import HandshakeUnit


class HandshakeHashRate(AlgoHashRateType):
    rate: float
    unit: HandshakeUnit = MinerAlgo.HANDSHAKE.unit.default

    def __float__(self):
        return float(self.rate)

    def __int__(self):
        return int(self.rate)

    def __repr__(self):
        return f"{self.rate} {str(self.unit)}"

    def __round__(self, n: int = None):
        return round(self.rate, n)

    def __add__(self, other: HandshakeHashRate | int | float) -> HandshakeHashRate:
        if isinstance(other, HandshakeHashRate):
            return HandshakeHashRate(
                rate=self.rate + other.into(self.unit).rate, unit=self.unit
            )
        return HandshakeHashRate(rate=self.rate + other, unit=self.unit)

    def __sub__(self, other: HandshakeHashRate | int | float) -> HandshakeHashRate:
        if isinstance(other, HandshakeHashRate):
            return HandshakeHashRate(
                rate=self.rate - other.into(self.unit).rate, unit=self.unit
            )
        return HandshakeHashRate(rate=self.rate - other, unit=self.unit)

    def __truediv__(self, other: HandshakeHashRate | int | float):
        if isinstance(other, HandshakeHashRate):
            return HandshakeHashRate(
                rate=self.rate / other.into(self.unit).rate, unit=self.unit
            )
        return HandshakeHashRate(rate=self.rate / other, unit=self.unit)

    def __floordiv__(self, other: HandshakeHashRate | int | float):
        if isinstance(other, HandshakeHashRate):
            return HandshakeHashRate(
                rate=self.rate // other.into(self.unit).rate, unit=self.unit
            )
        return HandshakeHashRate(rate=self.rate // other, unit=self.unit)

    def __mul__(self, other: HandshakeHashRate | int | float):
        if isinstance(other, HandshakeHashRate):
            return HandshakeHashRate(
                rate=self.rate * other.into(self.unit).rate, unit=self.unit
            )
        return HandshakeHashRate(rate=self.rate * other, unit=self.unit)

    def into(self, other: HandshakeUnit) -> HandshakeHashRate:
        return HandshakeHashRate(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
