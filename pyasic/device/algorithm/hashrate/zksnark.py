from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.zksnark import ZkSnarkUnit

from .unit import HashUnit


class ZkSnarkHashRate(AlgoHashRateType):
    rate: float
    unit: ZkSnarkUnit = HashUnit.ZKSNARK.default

    def into(self, other: ZkSnarkUnit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
