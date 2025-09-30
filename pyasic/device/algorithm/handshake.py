from __future__ import annotations

from .base import MinerAlgoType
from .hashrate.handshake import HandshakeHashRate
from .hashrate.unit.handshake import HandshakeUnit

__all__ = ["HandshakeAlgo", "HandshakeHashRate", "HandshakeUnit"]


# make this json serializable
class HandshakeAlgo(MinerAlgoType):
    hashrate: type[HandshakeHashRate] = HandshakeHashRate
    unit: type[HandshakeUnit] = HandshakeUnit

    name = "Handshake"
