from __future__ import annotations

from .base import MinerAlgoType
from .hashrate.kadena import KadenaHashRate
from .hashrate.unit.kadena import KadenaUnit

__all__ = ["KadenaAlgo", "KadenaHashRate", "KadenaUnit"]


# make this json serializable
class KadenaAlgo(MinerAlgoType):
    hashrate: type[KadenaHashRate] = KadenaHashRate
    unit: type[KadenaUnit] = KadenaUnit

    name = "Kadena"
