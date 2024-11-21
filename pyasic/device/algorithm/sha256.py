from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import SHA256HashRate
from .hashrate.unit import SHA256Unit


# make this json serializable
class SHA256Algo(MinerAlgoType):
    hashrate: type[SHA256HashRate] = SHA256HashRate
    unit: type[SHA256Unit] = SHA256Unit

    name = "SHA256"
