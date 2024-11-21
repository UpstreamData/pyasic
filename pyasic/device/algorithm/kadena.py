from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import KadenaHashRate
from .hashrate.unit import KadenaUnit


# make this json serializable
class KadenaAlgo(MinerAlgoType):
    hashrate: type[KadenaHashRate] = KadenaHashRate
    unit: type[KadenaUnit] = KadenaUnit

    name = "Kadena"
