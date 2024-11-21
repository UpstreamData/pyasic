from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import HandshakeHashRate
from .hashrate.unit import HandshakeUnit


# make this json serializable
class HandshakeAlgo(MinerAlgoType):
    hashrate: type[HandshakeHashRate] = HandshakeHashRate
    unit: type[HandshakeUnit] = HandshakeUnit

    name = "Handshake"
