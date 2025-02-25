from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import KHeavyHashHashRate
from .hashrate.unit import KHeavyHashUnit


# make this json serializable
class KHeavyHashAlgo(MinerAlgoType):
    hashrate: type[KHeavyHashHashRate] = KHeavyHashHashRate
    unit: type[KHeavyHashUnit] = KHeavyHashUnit

    name = "KHeavyHash"
