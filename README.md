# pyasic
*A simplified and standardized interface for Bitcoin ASICs.*

[![PyPI - Version](https://img.shields.io/pypi/v/pyasic.svg)](https://pypi.org/project/pyasic/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pyasic)](https://pypi.org/project/pyasic/)

[![Python - Supported Versions](https://img.shields.io/pypi/pyversions/pyasic.svg)](https://pypi.org/project/pyasic/)
[![CodeFactor - Grade](https://img.shields.io/codefactor/grade/github/UpstreamData/pyasic)](https://www.codefactor.io/repository/github/upstreamdata/pyasic)
[![Commit Activity - master](https://img.shields.io/github/commit-activity/y/UpstreamData/pyasic)](https://github.com/UpstreamData/pyasic/commits/master/)

[![Code Style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Read The Docs - Docs](https://img.shields.io/readthedocs/pyasic)](https://docs.pyasic.org)
[![License - Apache 2.0](https://img.shields.io/github/license/UpstreamData/pyasic)](https://github.com/UpstreamData/pyasic/blob/master/LICENSE.txt)

---
## Intro

Welcome to `pyasic`!  `pyasic` uses an asynchronous method of communicating with ASIC miners on your network, which makes it super fast.

[Click here to view supported miner types](https://docs.pyasic.org/en/latest/miners/supported_types/)

---
## Installation

It is recommended to install `pyasic` in a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/#what-other-popular-options-exist-aside-from-venv) to isolate it from the rest of your system. Options include:
  - [pypoetry](https://python-poetry.org/): the reccommended way, since pyasic already uses it by default

```
    poetry install
```

  - [venv](https://docs.python.org/3/library/venv.html): included in Python standard library but has fewer features than other options
  - [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv): [pyenv](https://github.com/pyenv/pyenv) plugin for managing virtualenvs

```
    pyenv install <python version number>
    pyenv virtualenv <python version number> <env name>
    pyenv activate <env name>
```

  - [conda](https://docs.conda.io/en/latest/)

##### Installing `pyasic`

`python -m pip install pyasic` or `poetry install`

##### Additional Developer Setup
```
poetry install --with dev
pre-commit install
```

---
## Getting started

Getting started with `pyasic` is easy.  First, find your miner (or miners) on the network by scanning for them or getting the correct class automatically for them if you know the IP.

##### Scanning for miners
To scan for miners in `pyasic`, we use the class `MinerNetwork`, which abstracts the search, communication, identification, setup, and return of a miner to 1 command.
The command `MinerNetwork.scan()` returns a list that contains any miners found.
```python
import asyncio  # asyncio for handling the async part
from pyasic.network import MinerNetwork  # miner network handles the scanning


async def scan_miners():  # define async scan function to allow awaiting
    # create a miner network
    # you can pass in any IP and it will use that in a subnet with a /24 mask (255 IPs).
    network = MinerNetwork.from_subnet("192.168.1.50/24")  # this uses the 192.168.1.0-255 network

    # scan for miners asynchronously
    # this will return the correct type of miners if they are supported with all functionality.
    miners = await network.scan()
    print(miners)

if __name__ == "__main__":
    asyncio.run(scan_miners())  # run the scan asynchronously with asyncio.run()
```

---
##### Creating miners based on IP
If you already know the IP address of your miner or miners, you can use the `MinerFactory` to communicate and identify the miners, or an abstraction of its functionality, `get_miner()`.
The function `get_miner()` will return any miner it found at the IP address specified, or an `UnknownMiner` if it cannot identify the miner.
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
    # gathering them will get them both at the same time
    # this makes it much faster to get a lot of miners at a time
    tasks = [get_miner("192.168.1.75"), get_miner("192.168.1.76")]
    miners = await asyncio.gather(*tasks)
    print(miners)


if __name__ == "__main__":
    asyncio.run(get_miners())  # get the miners asynchronously with asyncio.run()
```

---
## Data gathering

Once you have your miner(s) identified, you will likely want to get data from the miner(s).  You can do this using a built-in function in each miner called `get_data()`.
This function will return an instance of the dataclass `MinerData` with all data it can gather from the miner.
Each piece of data in a `MinerData` instance can be referenced by getting it as an attribute, such as `MinerData().hashrate`.

##### One miner
```python
import asyncio
from pyasic import get_miner

async def gather_miner_data():
    miner = await get_miner("192.168.1.75")
    if miner is not None:
        miner_data = await miner.get_data()
        print(miner_data)  # all data from the dataclass
        print(miner_data.hashrate)  # hashrate of the miner in TH/s

if __name__ == "__main__":
    asyncio.run(gather_miner_data())
```
---
##### Multiple miners
You can do something similar with multiple miners, with only needing to make a small change to get all the data at once.
```python
import asyncio  # asyncio for handling the async part
from pyasic.network import MinerNetwork  # miner network handles the scanning


async def gather_miner_data():  # define async scan function to allow awaiting
    network = MinerNetwork.from_subnet("192.168.1.50/24")
    miners = await network.scan()

    # we need to asyncio.gather() all the miners get_data() functions to make them run together
    all_miner_data = await asyncio.gather(*[miner.get_data() for miner in miners])

    for miner_data in all_miner_data:
        print(miner_data)    # print out all the data one by one

if __name__ == "__main__":
    asyncio.run(gather_miner_data())
```

---
## Miner control

`pyasic` exposes a standard interface for each miner using control functions.
Every miner class in `pyasic` must implement all the control functions defined in `BaseMiner`.

These functions are
`check_light`,
`fault_light_off`,
`fault_light_on`,
`get_config`,
`get_data`,
`get_errors`,
`get_hostname`,
`get_model`,
`reboot`,
`restart_backend`,
`stop_mining`,
`resume_mining`,
`is_mining`,
`send_config`, and
`set_power_limit`.

##### Usage
```python
import asyncio
from pyasic import get_miner


async def set_fault_light():
    miner = await get_miner("192.168.1.20")

    # call control function
    await miner.fault_light_on()

if __name__ == "__main__":
    asyncio.run(set_fault_light())
```

---
## Helper dataclasses

##### `MinerConfig` and `MinerData`

`pyasic` implements a few dataclasses as helpers to make data return types consistent across different miners and miner APIs.  The different fields of these dataclasses can all be viewed with the classmethod `cls.fields()`.

---

##### MinerData

`MinerData` is a return from the [`get_data()`](#get-data) function, and is used to have a consistent dataset across all returns.

You can call `MinerData.as_dict()` to get the dataclass as a dictionary, and there are many other helper functions contained in the class to convert to different data formats.

`MinerData` instances can also be added to each other to combine their data and can be divided by a number to divide all their data, allowing you to get average data from many miners by doing -
```python
from pyasic import MinerData

# examples of miner data
d1 = MinerData("192.168.1.1")
d2 = MinerData("192.168.1.2")

list_of_miner_data = [d1, d2]

average_data = sum(list_of_miner_data, start=MinerData("0.0.0.0"))/len(list_of_miner_data)
```

---

##### MinerConfig

`MinerConfig` is `pyasic`'s way to represent a configuration file from a miner.
It is designed to unionize the configuration of all supported miner types, and is the return from [`get_config()`](#get-config).

Each miner has a unique way to convert the `MinerConfig` to their specific type, there are helper functions in the class.
In most cases these helper functions should not be used, as [`send_config()`](#send-config) takes a [`MinerConfig` and will do the conversion to the right type for you.

You can use the `MinerConfig` as follows:
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

---
## Settings

`pyasic` has settings designed to make using large groups of miners easier.  You can set the default password for all types of miners using the `pyasic.settings` module, used as follows:

```python
from pyasic import settings

settings.update("default_antminer_web_password", "my_pwd")
```

##### Default values:
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
