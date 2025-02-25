from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import EtHashHashRate
from .hashrate.unit import EtHashUnit


class EtHashAlgo(MinerAlgoType):
    hashrate: type[EtHashHashRate] = EtHashHashRate
    unit: type[EtHashUnit] = EtHashUnit

    name = "EtHash"
