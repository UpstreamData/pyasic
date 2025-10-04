from __future__ import annotations

from .base import MinerAlgoType
from .hashrate.unit.zksnark import ZkSnarkUnit
from .hashrate.zksnark import ZkSnarkHashRate

__all__ = ["ZkSnarkAlgo", "ZkSnarkHashRate", "ZkSnarkUnit"]


class ZkSnarkAlgo(MinerAlgoType):
    hashrate: type[ZkSnarkHashRate] = ZkSnarkHashRate
    unit: type[ZkSnarkUnit] = ZkSnarkUnit

    name = "zkSNARK"
