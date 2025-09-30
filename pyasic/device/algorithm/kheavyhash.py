from __future__ import annotations

from .base import MinerAlgoType
from .hashrate.kheavyhash import KHeavyHashHashRate
from .hashrate.unit.kheavyhash import KHeavyHashUnit

__all__ = ["KHeavyHashAlgo", "KHeavyHashHashRate", "KHeavyHashUnit"]


# make this json serializable
class KHeavyHashAlgo(MinerAlgoType):
    hashrate: type[KHeavyHashHashRate] = KHeavyHashHashRate
    unit: type[KHeavyHashUnit] = KHeavyHashUnit

    name = "KHeavyHash"
