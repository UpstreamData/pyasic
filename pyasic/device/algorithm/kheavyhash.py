from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import KHeavyHashHashRate
from .hashrate.unit import KHeavyHashUnit


# make this json serializable
class _KHeavyHashAlgo(MinerAlgoType):
    hashrate = KHeavyHashHashRate
    unit = KHeavyHashUnit

    def __repr__(self):
        return "KHeavyHashAlgo"


KHeavyHashAlgo = _KHeavyHashAlgo("KHeavyHash")
