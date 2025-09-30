from __future__ import annotations

from .base import MinerAlgoType
from .hashrate.blockflow import BlockFlowHashRate
from .hashrate.unit.blockflow import BlockFlowUnit

__all__ = ["BlockFlowAlgo", "BlockFlowHashRate", "BlockFlowUnit"]


class BlockFlowAlgo(MinerAlgoType):
    hashrate: type[BlockFlowHashRate] = BlockFlowHashRate
    unit: type[BlockFlowUnit] = BlockFlowUnit

    name = "BlockFlow"
