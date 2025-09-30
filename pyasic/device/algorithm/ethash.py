from __future__ import annotations

from .base import MinerAlgoType
from .hashrate.ethash import EtHashHashRate
from .hashrate.unit.ethash import EtHashUnit

__all__ = ["EtHashAlgo", "EtHashHashRate", "EtHashUnit"]


class EtHashAlgo(MinerAlgoType):
    hashrate: type[EtHashHashRate] = EtHashHashRate
    unit: type[EtHashUnit] = EtHashUnit

    name = "EtHash"
