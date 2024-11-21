from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import KadenaHashRate
from .hashrate.unit import KadenaUnit


# make this json serializable
class _KadenaAlgo(MinerAlgoType):
    hashrate = KadenaHashRate
    unit = KadenaUnit

    def __repr__(self):
        return "KadenaAlgo"


KadenaAlgo = _KadenaAlgo("Kadena")
