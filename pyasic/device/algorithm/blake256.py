from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import Blake256HashRate
from .hashrate.unit import Blake256Unit


# make this json serializable
class _Blake256Algo(MinerAlgoType):
    hashrate = Blake256HashRate
    unit = Blake256Unit

    def __repr__(self):
        return "Blake256Algo"


Blake256Algo = _Blake256Algo("Blake256")
