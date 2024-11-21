from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import EquihashHashRate
from .hashrate.unit import EquihashUnit


# make this json serializable
class _EquihashAlgo(MinerAlgoType):
    hashrate = EquihashHashRate
    unit = EquihashUnit

    def __repr__(self):
        return "EquihashAlgo"


EquihashAlgo = _EquihashAlgo("Equihash")
