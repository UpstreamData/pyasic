# pyasic
## Base Miner
[`BaseMiner`][pyasic.miners.base.BaseMiner] is the basis for all miner classes, they all subclass (usually indirectly) from this class.

This class inherits from the [`MinerProtocol`][pyasic.miners.base.MinerProtocol], which outlines functionality for miners.

You may not instantiate this class on its own, only subclass from it.

::: pyasic.miners.base.BaseMiner
    handler: python
    options:
        heading_level: 4

::: pyasic.miners.base.MinerProtocol
    handler: python
    options:
        heading_level: 4
