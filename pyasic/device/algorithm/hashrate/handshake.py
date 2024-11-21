from __future__ import annotations

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.handshake import HandshakeUnit

from .unit import HashUnit


class HandshakeHashRate(AlgoHashRateType):
    rate: float
    unit: HandshakeUnit = HashUnit.HANDSHAKE.default

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
