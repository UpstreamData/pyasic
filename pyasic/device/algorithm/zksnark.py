from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import ZkSnarkHashRate
from .hashrate.unit import ZkSnarkUnit


class ZkSnarkAlgo(MinerAlgoType):
    hashrate: type[ZkSnarkHashRate] = ZkSnarkHashRate
    unit: type[ZkSnarkUnit] = ZkSnarkUnit

    name = "zkSNARK"
