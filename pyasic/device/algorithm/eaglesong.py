from __future__ import annotations

from .base import MinerAlgoType
from .hashrate.eaglesong import EaglesongHashRate
from .hashrate.unit.eaglesong import EaglesongUnit

__all__ = ["EaglesongAlgo", "EaglesongHashRate", "EaglesongUnit"]


# make this json serializable
class EaglesongAlgo(MinerAlgoType):
    hashrate: type[EaglesongHashRate] = EaglesongHashRate
    unit: type[EaglesongUnit] = EaglesongUnit

    name = "Eaglesong"
