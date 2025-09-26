from __future__ import annotations

from typing_extensions import Self

from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.algorithm.hashrate.unit.blockflow import BlockFlowUnit

from .unit import HashUnit


class BlockFlowHashRate(AlgoHashRateType[BlockFlowUnit]):
    rate: float
    unit: BlockFlowUnit = HashUnit.BLOCKFLOW.default

    def into(self, other: BlockFlowUnit) -> Self:
        return self.__class__(
            rate=self.rate / (other.value / self.unit.value), unit=other
        )
