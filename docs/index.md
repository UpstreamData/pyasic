# pyasic
*A set of modules for interfacing with many common types of ASIC bitcoin miners, using both their API and SSH.*

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pypi](https://img.shields.io/pypi/v/pyasic.svg)](https://pypi.org/project/pyasic/)
[![python](https://img.shields.io/pypi/pyversions/pyasic.svg)](https://pypi.org/project/pyasic/)
[![Read the Docs](https://img.shields.io/readthedocs/pyasic)](https://pyasic.readthedocs.io/en/latest/)
[![GitHub](https://img.shields.io/github/license/UpstreamData/pyasic)](https://github.com/UpstreamData/pyasic/blob/master/LICENSE.txt)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/UpstreamData/pyasic)](https://www.codefactor.io/repository/github/upstreamdata/pyasic)

## Intro
Welcome to pyasic!  Pyasic uses an asynchronous method of communicating with asic miners on your network, which makes it super fast.

[Supported Miner Types](miners/supported_types.md)

Getting started with pyasic is easy.  First, find your miner (or miners) on the network by scanning for them or getting the correct class automatically for them if you know the IP.

<br>

## Scanning for miners
To scan for miners in pyasic, we use the class [`MinerNetwork`][pyasic.network.MinerNetwork], which abstracts the search, communication, identification, setup, and return of a miner to 1 command.
The command [`MinerNetwork().scan_network_for_miners()`][pyasic.network.MinerNetwork.scan_network_for_miners] returns a list that contains any miners found.
```python
import asyncio  # asyncio for handling the async part
from pyasic.network import MinerNetwork  # miner network handles the scanning


async def scan_miners():  # define async scan function to allow awaiting
    # create a miner network
    # you can pass in any IP and it will use that in a subnet with a /24 mask (255 IPs).
    network = MinerNetwork("192.168.1.50")  # this uses the 192.168.1.0-255 network

    # scan for miners asynchronously
    # this will return the correct type of miners if they are supported with all functionality.
    miners = await network.scan_network_for_miners()
    print(miners)

if __name__ == "__main__":
    asyncio.run(scan_miners())  # run the scan asynchronously with asyncio.run()
```

<br>

## Creating miners based on IP
If you already know the IP address of your miner or miners, you can use the [`MinerFactory`][pyasic.miners.miner_factory.MinerFactory] to communicate and identify the miners, or an abstraction of its functionality, [`get_miner()`][pyasic.miners.get_miner].
The function [`get_miner()`][pyasic.miners.get_miner] will return any miner it found at the IP address specified, or an `UnknownMiner` if it cannot identify the miner.
```python
import asyncio  # asyncio for handling the async part
from pyasic import get_miner # handles miner creation


async def get_miners():  # define async scan function to allow awaiting
    # get the miner with the miner factory
    # the miner factory is a singleton, and will always use the same object and cache
    # this means you can always call it as MinerFactory().get_miner(), or just get_miner()
    miner_1 = await get_miner("192.168.1.75")
    miner_2 = await get_miner("192.168.1.76")
    print(miner_1, miner_2)

    # can also gather these, since they are async
    tasks = [get_miner("192.168.1.75"), get_miner("192.168.1.76")]
    miners = await asyncio.gather(*tasks)
    print(miners)


if __name__ == "__main__":
    asyncio.run(get_miners())  # get the miners asynchronously with asyncio.run()
```

<br>

## Getting data from miners

Once you have your miner(s) identified, you will likely want to get data from the miner(s).  You can do this using a built in function in each miner called `get_data()`.
This function will return an instance of the dataclass [`MinerData`][pyasic.data.MinerData] with all data it can gather from the miner.
Each piece of data in a [`MinerData`][pyasic.data.MinerData] instance can be referenced by getting it as an attribute, such as [`MinerData().hashrate`][pyasic.data.MinerData].
```python
import asyncio
from pyasic.miners.miner_factory import MinerFactory

async def gather_miner_data():
    miner = await MinerFactory().get_miner("192.168.1.75")
    miner_data = await miner.get_data()
    print(miner_data)  # all data from the dataclass
    print(miner_data.hashrate)  # hashrate of the miner in TH/s

if __name__ == "__main__":
    asyncio.run(gather_miner_data())
```

You can do something similar with multiple miners, with only needing to make a small change to get all the data at once.
```python
import asyncio  # asyncio for handling the async part
from pyasic.network import MinerNetwork  # miner network handles the scanning


async def gather_miner_data():  # define async scan function to allow awaiting
    network = MinerNetwork("192.168.1.50")
    miners = await network.scan_network_for_miners()

    # we need to asyncio.gather() all the miners get_data() functions to make them run together
    all_miner_data = await asyncio.gather(*[miner.get_data() for miner in miners])

    for miner_data in all_miner_data:
        print(miner_data)    # print out all the data one by one

if __name__ == "__main__":
    asyncio.run(gather_miner_data())
```

<br>

## Controlling miners via pyasic
Every miner class in pyasic must implement all the control functions defined in [`BaseMiner`][pyasic.miners.BaseMiner].

These functions are
[`check_light`](#check-light),
[`fault_light_off`](#fault-light-off),
[`fault_light_on`](#fault-light-on),
[`get_config`](#get-config),
[`get_data`](#get-data),
[`get_errors`](#get-errors),
[`get_hostname`](#get-hostname),
[`get_model`](#get-model),
[`reboot`](#reboot),
[`restart_backend`](#restart-backend),
[`stop_mining`](#stop-mining),
[`resume_mining`](#resume-mining),
[`is_mining`](#is-mining),
[`send_config`](#send-config), and
[`set_power_limit`](#set-power-limit).

<br>

### Check Light
::: pyasic.miners.BaseMiner.check_light
    handler: python
    options:
        heading_level: 4

<br>

### Fault Light Off
::: pyasic.miners.BaseMiner.fault_light_off
    handler: python
    options:
        heading_level: 4

<br>

### Fault Light On
::: pyasic.miners.BaseMiner.fault_light_on
    handler: python
    options:
        heading_level: 4

<br>

### Get Config
::: pyasic.miners.BaseMiner.get_config
    handler: python
    options:
        heading_level: 4

<br>

### Get Data
::: pyasic.miners.BaseMiner.get_data
    handler: python
    options:
        heading_level: 4

<br>

### Get Errors
::: pyasic.miners.BaseMiner.get_errors
    handler: python
    options:
        heading_level: 4

<br>

### Get Hostname
::: pyasic.miners.BaseMiner.get_hostname
    handler: python
    options:
        heading_level: 4

<br>

### Get Model
::: pyasic.miners.BaseMiner.get_model
    handler: python
    options:
        heading_level: 4

<br>

### Reboot
::: pyasic.miners.BaseMiner.reboot
    handler: python
    options:
        heading_level: 4

<br>

### Restart Backend
::: pyasic.miners.BaseMiner.restart_backend
    handler: python
    options:
        heading_level: 4

<br>

### Stop Mining
::: pyasic.miners.BaseMiner.stop_mining
    handler: python
    options:
        heading_level: 4

<br>

### Resume Mining
::: pyasic.miners.BaseMiner.resume_mining
    handler: python
    options:
        heading_level: 4

<br>

### Is Mining
::: pyasic.miners.BaseMiner.is_mining
    handler: python
    options:
        heading_level: 4

<br>

### Send Config
::: pyasic.miners.BaseMiner.send_config
    handler: python
    options:
        heading_level: 4

<br>

### Set Power Limit
::: pyasic.miners.BaseMiner.set_power_limit
    handler: python
    options:
        heading_level: 4

<br>

## [`MinerConfig`][pyasic.config.MinerConfig] and [`MinerData`][pyasic.data.MinerData]

Pyasic implements a few dataclasses as helpers to make data return types consistent across different miners and miner APIs.  The different fields of these dataclasses can all be viewed with the classmethod `cls.fields()`.

<br>

### [`MinerData`][pyasic.data.MinerData]

[`MinerData`][pyasic.data.MinerData] is a return from the [`get_data()`](#get-data) function, and is used to have a consistent dataset across all returns.

You can call [`MinerData.asdict()`][pyasic.data.MinerData.asdict] to get the dataclass as a dictionary, and there are many other helper functions contained in the class to convert to different data formats.

[`MinerData`][pyasic.data.MinerData] instances can also be added to each other to combine their data and can be divided by a number to divide all their data, allowing you to get average data from many miners by doing -
```python
from pyasic import MinerData

# examples of miner data
d1 = MinerData("192.168.1.1")
d2 = MinerData("192.168.1.2")

list_of_miner_data = [d1, d2]

average_data = sum(list_of_miner_data, start=MinerData("0.0.0.0"))/len(list_of_miner_data)
```


<br>

### [`MinerConfig`][pyasic.config.MinerConfig]

[`MinerConfig`][pyasic.config.MinerConfig] is pyasic's way to represent a configuration file from a miner.
It is the return from [`get_config()`](#get-config).

Each miner has a unique way to convert the [`MinerConfig`][pyasic.config.MinerConfig] to their specific type, there are helper functions in the class.
In most cases these helper functions should not be used, as [`send_config()`](#send-config) takes a [`MinerConfig`][pyasic.config.MinerConfig] and will do the conversion to the right type for you.
