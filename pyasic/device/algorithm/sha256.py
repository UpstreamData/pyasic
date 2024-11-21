from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import SHA256HashRate
from .hashrate.unit import SHA256Unit


# make this json serializable
class _SHA256Algo(MinerAlgoType):
    hashrate = SHA256HashRate
    unit = SHA256Unit

    def __repr__(self):
        return "SHA256Algo"


SHA256Algo = _SHA256Algo("SHA256")
