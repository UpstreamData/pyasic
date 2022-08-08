# pyasic
## Miner Network Range

[`MinerNetworkRange`][pyasic.network.net_range.MinerNetworkRange] is a class used by [`MinerNetwork`][pyasic.network.MinerNetwork] to handle any constructor stings.
The goal is to emulate what is produced by `ipaddress.ip_network` by allowing [`MinerNetwork`][pyasic.network.MinerNetwork] to get a list of hosts.
This allows this class to be the [`MinerNetwork.network`][pyasic.network.MinerNetwork] and hence be used for scanning.

::: pyasic.network.net_range.MinerNetworkRange
    handler: python
    options:
        show_root_heading: false
        heading_level: 4
