# pyasic
## Miner Factory

::: pyasic.miners.miner_factory.MinerFactory
    handler: python
    options:
        show_root_heading: false
        heading_level: 4
<br>

## Get Miner
::: pyasic.miners.get_miner
    handler: python
    options:
        show_root_heading: false
        heading_level: 4
<br>

## AnyMiner
::: pyasic.miners.miner_factory.AnyMiner
    handler: python
    options:
        show_root_heading: false
        heading_level: 4

[`AnyMiner`][pyasic.miners.miner_factory.AnyMiner] is a placeholder type variable used for typing returns of functions.
A function returning [`AnyMiner`][pyasic.miners.miner_factory.AnyMiner] will always return a subclass of [`BaseMiner`][pyasic.miners.BaseMiner],
and is used to specify a function returning some arbitrary type of miner class instance.
