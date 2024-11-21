from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import EquihashHashRate
from .hashrate.unit import EquihashUnit


# make this json serializable
class EquihashAlgo(MinerAlgoType):
    hashrate: type[EquihashHashRate] = EquihashHashRate
    unit: type[EquihashUnit] = EquihashUnit

    name = "Equihash"
