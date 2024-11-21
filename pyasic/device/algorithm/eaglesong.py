from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import EaglesongHashRate
from .hashrate.unit import EaglesongUnit


# make this json serializable
class _EaglesongAlgo(MinerAlgoType):
    hashrate = EaglesongHashRate
    unit = EaglesongUnit

    def __repr__(self):
        return "EaglesongAlgo"


EaglesongAlgo = _EaglesongAlgo("Eaglesong")
