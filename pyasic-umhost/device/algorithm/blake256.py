from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import Blake256HashRate
from .hashrate.unit import Blake256Unit


# make this json serializable
class Blake256Algo(MinerAlgoType):
    hashrate: type[Blake256HashRate] = Blake256HashRate
    unit: type[Blake256Unit] = Blake256Unit

    name = "Blake256"
