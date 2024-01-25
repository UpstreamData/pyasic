# pyasic
## Miner Factory

[`MinerFactory`][pyasic.MinerFactory] is the way to create miner types in `pyasic`.  The most important method is [`get_miner()`][pyasic.get_miner], which is mapped to [`pyasic.get_miner()`][pyasic.get_miner], and should be used from there.

The instance used for [`pyasic.get_miner()`][pyasic.get_miner] is `pyasic.miner_factory`.

[`MinerFactory`][pyasic.MinerFactory] also keeps a cache, which can be cleared if needed with `pyasic.miner_factory.clear_cached_miners()`.

Finally, there is functionality to get multiple miners without using `asyncio.gather()` explicitly.  Use `pyasic.miner_factory.get_multiple_miners()` with a list of IPs as strings to get a list of miner instances.  You can also get multiple miners with an `AsyncGenerator` by using `pyasic.miner_factory.get_miner_generator()`.

::: pyasic.miners.factory.MinerFactory
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
::: pyasic.miners.base.AnyMiner
    handler: python
    options:
        show_root_heading: false
        heading_level: 4

[`AnyMiner`][pyasic.miners.base.AnyMiner] is a placeholder type variable used for typing returns of functions.
A function returning [`AnyMiner`][pyasic.miners.base.AnyMiner] will always return a subclass of [`BaseMiner`][pyasic.miners.BaseMiner],
and is used to specify a function returning some arbitrary type of miner class instance.
