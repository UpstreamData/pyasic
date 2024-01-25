# pyasic
## Miner APIs
Each miner has a unique API that is used to communicate with it.
Each of these API types has commands that differ between them, and some commands have data that others do not.
Each miner that is a subclass of [`BaseMiner`][pyasic.miners.BaseMiner] should have an API linked to it as `Miner.api`.

All API implementations inherit from [`BaseMinerRPCAPI`][pyasic.rpc.base.BaseMinerRPCAPI], which implements the basic communications protocols.

[`BaseMinerRPCAPI`][pyasic.rpc.base.BaseMinerRPCAPI] should never be used unless inheriting to create a new miner API class for a new type of miner (which should be exceedingly rare).
[`BaseMinerRPCAPI`][pyasic.rpc.base.BaseMinerRPCAPI] cannot be instantiated directly, it will raise a `TypeError`.
Use these instead -

#### [BFGMiner API][pyasic.rpc.bfgminer.BFGMinerRPCAPI]
#### [BMMiner API][pyasic.rpc.bmminer.BMMinerRPCAPI]
#### [BOSMiner API][pyasic.rpc.bosminer.BOSMinerRPCAPI]
#### [BTMiner API][pyasic.rpc.btminer.BTMinerRPCAPI]
#### [CGMiner API][pyasic.rpc.cgminer.CGMinerRPCAPI]
#### [LUXMiner API][pyasic.rpc.luxminer.LUXMinerRPCAPI]
#### [Unknown API][pyasic.rpc.unknown.UnknownRPCAPI]

<br>

## BaseMinerRPCAPI
::: pyasic.rpc.base.BaseMinerRPCAPI
    handler: python
    options:
        heading_level: 4
