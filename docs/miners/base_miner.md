# pyasic
## Base Miner
[`BaseMiner`][pyasic.miners.BaseMiner] is the basis for all miner classes, they all subclass (usually indirectly) from this class.

You may not instantiate this class on its own, only subclass from it.  Trying to instantiate an instance of this class will raise `TypeError`.

::: pyasic.miners.BaseMiner
    handler: python
    options:
        heading_level: 4
