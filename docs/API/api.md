# pyasic
## Miner APIs
Each miner has a unique API that is used to communicate with it.
Each of these API types has commands that differ between them, and some commands have data that others do not.
Each miner that is a subclass of [`BaseMiner`][pyasic.miners.BaseMiner] should have an API linked to it as `Miner.api`.

All API implementations inherit from [`BaseMinerRPCAPI`][pyasic.API.BaseMinerRPCAPI], which implements the basic communications protocols.

[`BaseMinerRPCAPI`][pyasic.API.BaseMinerRPCAPI] should never be used unless inheriting to create a new miner API class for a new type of miner (which should be exceedingly rare).
[`BaseMinerRPCAPI`][pyasic.API.BaseMinerRPCAPI] cannot be instantiated directly, it will raise a `TypeError`.
Use these instead -

#### [BFGMiner API][pyasic.API.bfgminer.BFGMinerRPCAPI]
#### [BMMiner API][pyasic.API.bmminer.BMMinerRPCAPI]
#### [BOSMiner API][pyasic.API.bosminer.BOSMinerRPCAPI]
#### [BTMiner API][pyasic.API.btminer.BTMinerRPCAPI]
#### [CGMiner API][pyasic.API.cgminer.CGMinerRPCAPI]
#### [LUXMiner API][pyasic.API.luxminer.LUXMinerRPCAPI]
#### [Unknown API][pyasic.API.unknown.UnknownRPCAPI]

<br>

## BaseMinerRPCAPI
::: pyasic.API.BaseMinerRPCAPI
    handler: python
    options:
        heading_level: 4
