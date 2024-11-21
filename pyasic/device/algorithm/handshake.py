from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import HandshakeHashRate
from .hashrate.unit import HandshakeUnit


# make this json serializable
class _HandshakeAlgo(MinerAlgoType):
    hashrate = HandshakeHashRate
    unit = HandshakeUnit

    def __repr__(self):
        return "HandshakeAlgo"


HandshakeAlgo = _HandshakeAlgo("Handshake")
