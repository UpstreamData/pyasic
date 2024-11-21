from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import ScryptHashRate
from .hashrate.unit import ScryptUnit


# make this json serializable
class _ScryptAlgo(MinerAlgoType):
    hashrate = ScryptHashRate
    unit = ScryptUnit

    def __repr__(self):
        return "ScryptAlgo"


ScryptAlgo = _ScryptAlgo("Scrypt")
