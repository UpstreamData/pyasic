# pyasic
## Miner APIs
Each miner has a unique API that is used to communicate with it.
Each of these API types has commands that differ between them, and some commands have data that others do not.
Each miner that is a subclass of [`BaseMiner`][pyasic.miners.BaseMiner] should have an API linked to it as `Miner.api`.

All API implementations inherit from [`BaseMinerAPI`][pyasic.API.BaseMinerAPI], which implements the basic communications protocols.

[`BaseMinerAPI`][pyasic.API.BaseMinerAPI] should never be used unless inheriting to create a new miner API class for a new type of miner (which should be exceedingly rare).
[`BaseMinerAPI`][pyasic.API.BaseMinerAPI] cannot be instantiated directly, it will raise a `TypeError`.
Use these instead -

#### [BFGMiner API][pyasic.API.bfgminer.BFGMinerAPI]
#### [BMMiner API][pyasic.API.bmminer.BMMinerAPI]
#### [BOSMiner API][pyasic.API.bosminer.BOSMinerAPI]
#### [BTMiner API][pyasic.API.btminer.BTMinerAPI]
#### [CGMiner API][pyasic.API.cgminer.CGMinerAPI]
#### [LUXMiner API][pyasic.API.luxminer.LUXMinerAPI]
#### [Unknown API][pyasic.API.unknown.UnknownAPI]

<br>

## BaseMinerAPI
::: pyasic.API.BaseMinerAPI
    handler: python
    options:
        heading_level: 4
