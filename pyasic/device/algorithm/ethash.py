from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import EtHashHashRate
from .hashrate.unit import EtHashUnit


# make this json serializable
class _EtHashAlgo(MinerAlgoType):
    hashrate = EtHashHashRate
    unit = EtHashUnit

    def __repr__(self):
        return "EtHashAlgo"


EtHashAlgo = _EtHashAlgo("EtHash")
