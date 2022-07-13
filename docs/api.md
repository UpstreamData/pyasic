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

## BOSMinerAPI
::: pyasic.API.bosminer.BOSMinerAPI
    handler: python
    options:
        show_root_heading: false
        heading_level: 4

## BTMinerAPI
::: pyasic.API.btminer.BTMinerAPI
    handler: python
    options:
        show_root_heading: false
        heading_level: 4

## CGMinerAPI
::: pyasic.API.cgminer.CGMinerAPI
    handler: python
    options:
        show_root_heading: false
        heading_level: 4

## UnknownAPI
::: pyasic.API.unknown.UnknownAPI
    handler: python
    options:
        show_root_heading: false
        heading_level: 4
