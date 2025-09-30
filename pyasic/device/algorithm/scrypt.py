from __future__ import annotations

from .base import MinerAlgoType
from .hashrate.scrypt import ScryptHashRate
from .hashrate.unit.scrypt import ScryptUnit

__all__ = ["ScryptAlgo", "ScryptHashRate", "ScryptUnit"]


class ScryptAlgo(MinerAlgoType):
    hashrate: type[ScryptHashRate] = ScryptHashRate
    unit: type[ScryptUnit] = ScryptUnit

    name = "Scrypt"
