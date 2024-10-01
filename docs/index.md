# pyasic
*A simplified and standardized interface for Bitcoin ASICs.*


[![PyPI - Version](https://img.shields.io/pypi/v/pyasic.svg)](https://pypi.org/project/pyasic/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pyasic)](https://pypi.org/project/pyasic/)
[![Python - Supported Versions](https://img.shields.io/pypi/pyversions/pyasic.svg)](https://pypi.org/project/pyasic/)
[![CodeFactor - Grade](https://img.shields.io/codefactor/grade/github/UpstreamData/pyasic)](https://www.codefactor.io/repository/github/upstreamdata/pyasic)
[![Commit Activity - master](https://img.shields.io/github/commit-activity/y/UpstreamData/pyasic)](https://github.com/UpstreamData/pyasic/commits/master/)
[![Code Style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Read The Docs - Docs](https://img.shields.io/readthedocs/pyasic)](https://pyasic.readthedocs.io/en/latest/)
[![License - Apache 2.0](https://img.shields.io/github/license/UpstreamData/pyasic)](https://github.com/UpstreamData/pyasic/blob/master/LICENSE.txt)

## Intro
---
Welcome to `pyasic`!  `pyasic` uses an asynchronous method of communicating with ASIC miners on your network, which makes it super fast.

[Click here to view supported miner types](miners/supported_types.md)

## Installation
---
It is recommended to install `pyasic` in a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/#what-other-popular-options-exist-aside-from-venv) to isolate it from the rest of your system.
`pyasic` can be installed directly from pip, either with `pip install pyasic`, or a different command if using a tool like `pypoetry`.

## Getting started
---
Getting started with `pyasic` is easy.  First, find your miner (or miners) on the network by scanning for them or getting the correct class automatically for them if you know the IP.

### Scanning for miners
To scan for miners in `pyasic`, we use the class [`MinerNetwork`][pyasic.network.MinerNetwork], which abstracts the search, communication, identification, setup, and return of a miner to 1 command.
The command [`MinerNetwork.scan()`][pyasic.network.MinerNetwork.scan] returns a list that contains any miners found.
```python3
import asyncio# (1)!
from pyasic.network import MinerNetwork# (2)!


async def scan_miners():# (3)!
    network = MinerNetwork.from_subnet("192.168.1.50/24")# (4)!

    miners = await network.scan()# (5)!
    print(miners)

if __name__ == "__main__":
    asyncio.run(scan_miners())# (6)!
```

1. `asyncio` for handling the async part.
2. `MinerNetwork` handles the scanning.
3. Define an async function to allow awaiting.
4. Create a miner network.
You can pass in any IP and it will use that in a subnet with a /24 mask (255 IPs).
This uses the 192.168.1.0-255 network.
5. Scan for miners asynchronously.
This will return the correct type of miners (if they are supported) with all functionality.
6. Run the scan asynchronously with asyncio.run().

---
### Creating miners based on IP
If you already know the IP address of your miner or miners, you can use the [`MinerFactory`][pyasic.miners.factory.MinerFactory] to communicate and identify the miners, or an abstraction of its functionality, [`get_miner()`][pyasic.miners.get_miner].
The function [`get_miner()`][pyasic.miners.get_miner] will return any miner it found at the IP address specified, or an `UnknownMiner` if it cannot identify the miner.
```python
import asyncio# (1)!
from pyasic import get_miner# (2)!


async def get_miners():# (3)!
    miner_1 = await get_miner("192.168.1.75")# (4)!
    miner_2 = await get_miner("192.168.1.76")
    print(miner_1, miner_2)

    tasks = [get_miner("192.168.1.75"), get_miner("192.168.1.76")]
    miners = await asyncio.gather(*tasks)# (5)!
    print(miners)


if __name__ == "__main__":
    asyncio.run(get_miners())# (6)!
```

1. `asyncio` for handling the async part.
2. `get_miner` handles the miner type selection.
3. Define an async function to allow awaiting.
4. Get the miner.
5. Can also gather these, since they are async.
Gathering them will get them both at the same time.
This makes it much faster to get a lot of miners at a time.
6. Get the miners asynchronously with asyncio.run().

## Data gathering
---
Once you have your miner(s) identified, you will likely want to get data from the miner(s).  You can do this using a built-in function in each miner called `get_data()`.
This function will return an instance of the dataclass [`MinerData`][pyasic.data.MinerData] with all data it can gather from the miner.
Each piece of data in a [`MinerData`][pyasic.data.MinerData] instance can be referenced by getting it as an attribute, such as [`MinerData().hashrate`][pyasic.data.MinerData].

### One miner
```python
import asyncio# (1)!
from pyasic import get_miner# (2)!


async def gather_miner_data():# (3)!
    miner = await get_miner("192.168.1.75")# (4)!
    if miner is not None:# (5)!
        miner_data = await miner.get_data()# (6)!
        print(miner_data)# (7)!
        print(miner_data.hashrate)  # hashrate of the miner in TH/s

if __name__ == "__main__":
    asyncio.run(gather_miner_data())# (9)!
```

1. `asyncio` for handling the async part.
2. `get_miner` handles the miner type selection.
3. Define an async function to allow awaiting.
4. Get the miner.
5. Make sure the miner exists.
If this result is `None`, the miner may be offline.
6. Get data from the miner.
7. All the data from the dataclass.
8. Hashrate of the miner, with unit information.
9. Get the miner data asynchronously with asyncio.run().

### Multiple miners
You can do something similar with multiple miners, with only needing to make a small change to get all the data at once.
```python
import asyncio# (1)!
from pyasic.network import MinerNetwork# (2)!


async def gather_miner_data():# (3)!
    network = MinerNetwork.from_subnet("192.168.1.50/24")# (4)!
    miners = await network.scan()# (5)!

    all_miner_data = await asyncio.gather(*[miner.get_data() for miner in miners])

    for miner_data in all_miner_data:
        print(miner_data)# (7)!

if __name__ == "__main__":
    asyncio.run(gather_miner_data())# (8)!
```

1. `asyncio` for handling the async part.
2. `MinerNetwork` handles the scanning.
3. Define an async function to allow awaiting.
4. Create a miner network.
5. Scan for miners asynchronously.
6. Use `asyncio.gather()` with all the miners' `get_data()` functions to make them run together.
7. Print out the data one at a time.
8. Get the miner data asynchronously with asyncio.run().

## Miner control
---
`pyasic` exposes a standard interface for each miner using control functions.
Every miner class in `pyasic` must implement all the following control functions.

[`check_light`][pyasic.miners.base.MinerProtocol.check_light],
[`fault_light_off`][pyasic.miners.base.MinerProtocol.fault_light_off],
[`fault_light_on`][pyasic.miners.base.MinerProtocol.fault_light_on],
[`get_config`][pyasic.miners.base.MinerProtocol.get_config],
[`get_data`][pyasic.miners.base.MinerProtocol.get_data],
[`get_errors`][pyasic.miners.base.MinerProtocol.get_errors],
[`get_hostname`][pyasic.miners.base.MinerProtocol.get_hostname],
[`get_model`][pyasic.miners.base.MinerProtocol.get_model],
[`reboot`][pyasic.miners.base.MinerProtocol.reboot],
[`restart_backend`][pyasic.miners.base.MinerProtocol.restart_backend],
[`stop_mining`][pyasic.miners.base.MinerProtocol.stop_mining],
[`resume_mining`][pyasic.miners.base.MinerProtocol.resume_mining],
[`is_mining`][pyasic.miners.base.MinerProtocol.is_mining],
[`send_config`][pyasic.miners.base.MinerProtocol.send_config], and
[`set_power_limit`][pyasic.miners.base.MinerProtocol.set_power_limit].

### Usage
```python
import asyncio# (1)!
from pyasic import get_miner# (2)!


async def set_fault_light():# (3)!
    miner = await get_miner("192.168.1.20")# (4)!

    await miner.fault_light_on()# (5)!

if __name__ == "__main__":
    asyncio.run(set_fault_light())# (6)!
```

1. `asyncio` for handling the async part.
2. `get_miner` handles the miner type selection.
3. Define an async function to allow awaiting.
4. Get the miner.
5. Call the miner control function.
6. Call the control function asynchronously with asyncio.run().


## Helper dataclasses
---

### [`MinerConfig`][pyasic.config.MinerConfig] and [`MinerData`][pyasic.data.MinerData]

`pyasic` implements a few dataclasses as helpers to make data return types consistent across different miners and miner APIs.  The different fields of these dataclasses can all be viewed with the classmethod `cls.fields()`.

---

### [`MinerData`][pyasic.data.MinerData]

[`MinerData`][pyasic.data.MinerData] is a return from the [`get_data()`][pyasic.miners.base.MinerProtocol.get_data] function, and is used to have a consistent dataset across all returns.

You can call [`MinerData.as_dict()`][pyasic.data.MinerData.as_dict] to get the dataclass as a dictionary, and there are many other helper functions contained in the class to convert to different data formats.

[`MinerData`][pyasic.data.MinerData] instances can also be added to each other to combine their data and can be divided by a number to divide all their data, allowing you to get average data from many miners by doing -
```python
from pyasic import MinerData

# examples of miner data
d1 = MinerData("192.168.1.1")
d2 = MinerData("192.168.1.2")

list_of_miner_data = [d1, d2]

average_data = sum(list_of_miner_data, start=MinerData("0.0.0.0"))/len(list_of_miner_data)
```

---

### [`MinerConfig`][pyasic.config.MinerConfig]

[`MinerConfig`][pyasic.config.MinerConfig] is `pyasic`'s way to represent a configuration file from a miner.
It is designed to unionize the configuration of all supported miner types, and is the return from [`get_config()`][pyasic.miners.base.MinerProtocol.get_config].

Each miner has a unique way to convert the [`MinerConfig`][pyasic.config.MinerConfig] to their specific type, there are helper functions in the class.
In most cases these helper functions should not be used, as [`send_config()`][pyasic.miners.base.MinerProtocol.send_config] takes a [`MinerConfig`][pyasic.config.MinerConfig] and will do the conversion to the right type for you.

You can use the [`MinerConfig`][pyasic.config.MinerConfig] as follows:
```python
import asyncio
from pyasic import get_miner


async def set_fault_light():
    miner = await get_miner("192.168.1.20")

    # get config
    cfg = await miner.get_config()

    # send config
    await miner.send_config(cfg)

if __name__ == "__main__":
    asyncio.run(set_fault_light())

```

## Settings
---
`pyasic` has settings designed to make using large groups of miners easier.  You can set the default password for all types of miners using the `pyasic.settings` module, used as follows:

```python
from pyasic import settings

settings.update("default_antminer_web_password", "my_pwd")
```

### Default values:
```
"network_ping_retries": 1,
"network_ping_timeout": 3,
"network_scan_semaphore": None,
"factory_get_retries": 1,
"factory_get_timeout": 3,
"get_data_retries": 1,
"api_function_timeout": 5,
"antminer_mining_mode_as_str": False,
"default_whatsminer_rpc_password": "admin",
"default_innosilicon_web_password": "admin",
"default_antminer_web_password": "root",
"default_bosminer_web_password": "root",
"default_vnish_web_password": "admin",
"default_goldshell_web_password": "123456789",
"default_auradine_web_password": "admin",
"default_epic_web_password": "letmein",
"default_hive_web_password": "admin",
"default_antminer_ssh_password": "miner",
"default_bosminer_ssh_password": "root",

# ADVANCED
# Only use this if you know what you are doing
"socket_linger_time": 1000,
```
