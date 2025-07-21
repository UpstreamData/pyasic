from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import BlockFlowHashRate
from .hashrate.unit import BlockFlowUnit


class BlockFlowAlgo(MinerAlgoType):
    hashrate: type[BlockFlowHashRate] = BlockFlowHashRate
    unit: type[BlockFlowUnit] = BlockFlowUnit

    name = "BlockFlow"
