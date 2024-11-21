from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import ScryptHashRate
from .hashrate.unit import ScryptUnit


class ScryptAlgo(MinerAlgoType):
    hashrate: type[ScryptHashRate] = ScryptHashRate
    unit: type[ScryptUnit] = ScryptUnit

    name = "Scrypt"
