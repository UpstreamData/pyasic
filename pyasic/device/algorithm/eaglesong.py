from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import EaglesongHashRate
from .hashrate.unit import EaglesongUnit


# make this json serializable
class EaglesongAlgo(MinerAlgoType):
    hashrate: type[EaglesongHashRate] = EaglesongHashRate
    unit: type[EaglesongUnit] = EaglesongUnit

    name = "Eaglesong"
