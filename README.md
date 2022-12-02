# pyasic
*A set of modules for interfacing with many common types of ASIC bitcoin miners, using both their API and SSH.*

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pypi](https://img.shields.io/pypi/v/pyasic.svg)](https://pypi.org/project/pyasic/)
[![python](https://img.shields.io/pypi/pyversions/pyasic.svg)](https://pypi.org/project/pyasic/)
[![Read the Docs](https://img.shields.io/readthedocs/pyasic)](https://pyasic.readthedocs.io/en/latest/)
[![GitHub](https://img.shields.io/github/license/UpstreamData/pyasic)](https://github.com/UpstreamData/pyasic/blob/master/LICENSE.txt)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/UpstreamData/pyasic)](https://www.codefactor.io/repository/github/upstreamdata/pyasic)
## Documentation and Supported Miners
Documentation is located on Read the Docs as [pyasic](https://pyasic.readthedocs.io/en/latest/).

Supported miners are listed in the docs, [here](https://pyasic.readthedocs.io/en/latest/miners/supported_types/).

## Installation
You can install pyasic directly from pip with the command `pip install pyasic`.

For those of you who aren't comfortable with code and developer tools, there are windows builds of GUI applications that use this library [here](https://drive.google.com/drive/folders/1DjR8UOS_g0ehfiJcgmrV0FFoqFvE9akW?usp=sharing).

## Developer Setup
It is highly reccommended that you contribute to this project through [`pyasic-super`](https://github.com/UpstreamData/pyasic-super) using its submodules.  This allows testing in conjunction with other `pyasic` related programs.

<br>

This repo uses poetry for dependencies, which can be installed by following the guide on their website [here](https://python-poetry.org/docs/#installation).

After you have poetry installed, run `poetry install --with dev`, or `poetry install --with dev,docs` if you want to include packages required for documentation.

Finally, initialize pre-commit hooks with `poetry run pre-commit install`.

### Documentation Testing
Testing the documentation can be done by running `poetry run mkdocs serve`, whcih will serve the documentation locally on port 8000.

## Interfacing with miners programmatically

There are 2 main ways to get a miner (and the functions attached to it), via scanning or via the `MinerFactory()`.

#### Scanning for miners
```python
import asyncio

from pyasic.network import MinerNetwork


# define asynchronous function to scan for miners
async def scan_and_get_data():
    # Define network range to be used for scanning
    # This can take a list of IPs, a constructor string, or an IP and subnet mask
    # The standard mask is /24 (x.x.x.0-255), and you can pass any IP address in the subnet
    net = MinerNetwork("192.168.1.69", mask=24)
    # Scan the network for miners
    # This function returns a list of miners of the correct type as a class
    miners: list = await net.scan_network_for_miners()

    # We can now get data from any of these miners
    # To do them all we have to create a list of tasks and gather them
    tasks = [miner.get_data() for miner in miners]
    # Gather all tasks asynchronously and run them
    data = await asyncio.gather(*tasks)

    # Data is now a list of MinerData, and we can reference any part of that
    # Print out all data for now
    for item in data:
        print(item)

if __name__ == "__main__":
    asyncio.run(scan_and_get_data())
```


#### Getting a miner if you know the IP
```python
import asyncio

from pyasic import get_miner


# define asynchronous function to get miner and data
async def get_miner_data(miner_ip: str):
    # Use MinerFactory to get miner
    # MinerFactory is a singleton, so we can just get the instance in place
    miner = await get_miner(miner_ip)

    # Get data from the miner
    data = await miner.get_data()
    print(data)

if __name__ == "__main__":
    asyncio.run(get_miner_data("192.168.1.69"))
```

### Advanced data gathering

If needed, this library exposes a wrapper for the miner API that can be used for advanced data gathering.

You can see more information on basic usage of the APIs past this example in the docs [here](https://pyasic.readthedocs.io/en/latest/API/api/).

Please see the appropriate API documentation page (pyasic docs -> Advanced -> Miner APIs -> your API type) for a link to that specific miner's API documentation page and more information.

#### List available API commands
```python
import asyncio

from pyasic import get_miner


async def get_api_commands(miner_ip: str):
    # Get the miner
    miner = await get_miner(miner_ip)

    # List all available commands
    # Can also be called explicitly with the function miner.api.get_commands()
    print(miner.api.commands)


if __name__ == "__main__":
    asyncio.run(get_api_commands("192.168.1.69"))
```

#### Use miner API commands to gather data

The miner API commands will raise an `APIError` if they fail with a bad status code, to bypass this you must send them manually by using `miner.api.send_command(command, ignore_errors=True)`

```python
import asyncio

from pyasic import get_miner


async def get_api_commands(miner_ip: str):
    # Get the miner
    miner = await get_miner(miner_ip)

    # Run the devdetails command
    # This is equivalent to await miner.api.send_command("devdetails")
    devdetails: dict = await miner.api.devdetails()
    print(devdetails)


if __name__ == "__main__":
    asyncio.run(get_api_commands("192.168.1.69"))
```
