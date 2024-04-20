# pyasic
## Miner Web APIs
Each miner has a unique Web API that is used to communicate with it.
Each of these API types has commands that differ between them, and some commands have data that others do not.
Each miner that is a subclass of [`BaseMiner`][pyasic.miners.base.BaseMiner] may have an API linked to it as `Miner.web`.

All API implementations inherit from [`BaseWebAPI`][pyasic.web.BaseWebAPI], which implements the basic communications protocols.

[`BaseWebAPI`][pyasic.web.BaseWebAPI] should never be used unless inheriting to create a new miner API class for a new type of miner (which should be exceedingly rare).
Use these instead -

#### [AntminerModerNWebAPI][pyasic.web.antminer.AntminerModernWebAPI]
#### [AntminerOldWebAPI][pyasic.web.antminer.AntminerOldWebAPI]
#### [AuradineWebAPI][pyasic.web.auradine.AuradineWebAPI]
#### [ePICWebAPI][pyasic.web.epic.ePICWebAPI]
#### [GoldshellWebAPI][pyasic.web.goldshell.GoldshellWebAPI]
#### [InnosiliconWebAPI][pyasic.web.innosilicon.InnosiliconWebAPI]
#### [MaraWebAPI][pyasic.web.marathon.MaraWebAPI]
#### [VNishWebAPI][pyasic.web.vnish.VNishWebAPI]

<br>

## BaseWebAPI
::: pyasic.web.BaseWebAPI
    handler: python
    options:
        heading_level: 4
