# pyasic
*A set of modules for interfacing with many common types of ASIC bitcoin miners, using both their API and SSH.*

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code style: black](https://img.shields.io/pypi/v/pyasic.svg)](https://pypi.org/project/pyasic/)
[![Code style: black](https://img.shields.io/pypi/pyversions/pyasic.svg)](https://pypi.org/project/pyasic/)

## Intro
Welcome to pyasic!  Pyasic uses an asynchronous method of communicating with asic miners on your network, which makes it super fast.

Getting started with pyasic is easy.  First, find your miner (or miners) on the network by scanning for them or getting the correct class automatically for them if you know the IP.

<br>

## Scanning for miners
To scan for miners in pyasic, we use the class `MinerNetwork`, which abstracts the search, communication, identification, setup, and return of a miner to 1 command.
The command `MinerNetwork().scan_network_for_miners()` returns a list that contains any miners found.
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
If you already know the IP address of your miner or miners, you can use the `MinerFactory` to communicate and identify the miners.
The function `MinerFactory().get_miner()` will return any miner it found at the IP address specified, or an `UnknownMiner` if it cannot identify the miner.
```python
import asyncio  # asyncio for handling the async part
from pyasic.miners.miner_factory import MinerFactory  # miner factory handles miners creation


async def get_miners():  # define async scan function to allow awaiting
    # get the miner with miner factory
    # miner factory is a singleton, and will always use the same object and cache
    # this means you can always call it as MinerFactory().get_miner()
    miner_1 = await MinerFactory().get_miner("192.168.1.75")
    miner_2 = await MinerFactory().get_miner("192.168.1.76")
    print(miner_1, miner_2)
    
if __name__ == "__main__": 
    asyncio.run(get_miners())  # get the miners asynchronously with asyncio.run()
```

<br>

## Getting data from miners

Once you have your miner(s) identified, you will likely want to get data from the miner(s).  You can do this using a built in function in each miner called `get_data()`.
This function will return a instance of the dataclass `MinerData` with all data it can gather from the miner.
Each piece of data in a `MinerData` instance can be referenced by getting it as an attribute, such as `MinerData().hashrate`
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
