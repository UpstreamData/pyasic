from __future__ import annotations

from .base import MinerAlgoType
from .hashrate.equihash import EquihashHashRate
from .hashrate.unit.equihash import EquihashUnit

__all__ = ["EquihashAlgo", "EquihashHashRate", "EquihashUnit"]


# make this json serializable
class EquihashAlgo(MinerAlgoType):
    hashrate: type[EquihashHashRate] = EquihashHashRate
    unit: type[EquihashUnit] = EquihashUnit

    name = "Equihash"
