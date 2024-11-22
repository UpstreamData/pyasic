from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.handshake import HandshakeUnit

from .unit import HashUnit


class HandshakeHashRate(AlgoHashRateType):
    rate: float
    unit: HandshakeUnit = HashUnit.HANDSHAKE.default

    def into(self, other: HandshakeUnit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
