# pyasic
## Miner APIs
Each miner has a unique API that is used to communicate with it.
Each of these API types has commands that differ between them, and some commands have data that others do not.
Each miner that is a subclass of `BaseMiner` should have an API linked to it as `Miner.api`.

All API implementations inherit from `BaseMinerAPI`, which implements the basic communications protocols.

## BMMinerAPI
::: pyasic.API.bmminer.BMMinerAPI
    handler: python
    options:
        show_root_heading: false
        heading_level: 4
