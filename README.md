# pyasic
*A set of modules for interfacing with many common types of ASIC bitcoin miners, using both their API and SSH.*

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pypi](https://img.shields.io/pypi/v/pyasic.svg)](https://pypi.org/project/pyasic/)
[![python](https://img.shields.io/pypi/pyversions/pyasic.svg)](https://pypi.org/project/pyasic/)
[![Read the Docs](https://img.shields.io/readthedocs/pyasic)](https://pyasic.readthedocs.io/en/latest/)
[![GitHub](https://img.shields.io/github/license/UpstreamData/pyasic)](https://github.com/UpstreamData/pyasic/blob/master/LICENSE.txt)
[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/UpstreamData/pyasic)](https://www.codefactor.io/repository/github/upstreamdata/pyasic)
## Documentation
Documentation is located on Read the Docs as [pyasic](https://pyasic.readthedocs.io/en/latest/)

## Usage

### Standard Usage
You can install pyasic directly from pip with the command `pip install pyasic`

For those of you who aren't comfortable with code and developer tools, there are windows builds of GUI applications that use this library here -> (https://drive.google.com/drive/folders/1DjR8UOS_g0ehfiJcgmrV0FFoqFvE9akW?usp=sharing)

### Developers
To use this repo, first download it, create a virtual environment, enter the virtual environment, and install relevant packages by navigating to this directory and running ```pip install -r requirements.txt``` on Windows or ```pip3 install -r requirements.txt``` on Mac or UNIX if the first command fails.

You can also use poetry by initializing and running ```poetry install```

### Interfacing with miners programmatically

##### Note: If you are trying to interface with Whatsminers, there is a bug in the way they are interacted with on Windows, so to fix that you need to change the event loop policy using this code: 
```python
# need to import these 2 libraries, you need asyncio anyway so make sure you have sys imported
import sys
import asyncio

# if the computer is windows, set the event loop policy to a WindowsSelector policy
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

##### It is likely a good idea to use this code in your program anyway to be preventative.
<br>

To write your own custom programs with this repo, you have many options.

It is recommended that you explore the files in this repo to familiarize yourself with them, try starting with the miners module and going from there.

There are 2 main ways to get a miner and it's functions via scanning or via the MinerFactory.

#### Scanning for miners
```python
import asyncio
import sys

from pyasic.network import MinerNetwork

# Fix whatsminer bug
# if the computer is windows, set the event loop policy to a WindowsSelector policy
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# define asynchronous function to scan for miners
async def scan_and_get_data():
    # Define network range to be used for scanning
    # This can take a list of IPs, a constructor string, or an IP and subnet mask
    # The standard mask is /24, and you can pass any IP address in the subnet
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

</br>

#### Getting a miner if you know the IP
```python
import asyncio
import sys

from pyasic.miners.miner_factory import MinerFactory

# Fix whatsminer bug
# if the computer is windows, set the event loop policy to a WindowsSelector policy
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# define asynchronous function to get miner and data
async def get_miner_data(miner_ip: str):
    # Use MinerFactory to get miner
    # MinerFactory is a singleton, so we can just get the instance in place
    miner = await MinerFactory().get_miner(miner_ip)
    
    # Get data from the miner
    data = await miner.get_data()
    print(data)

if __name__ == "__main__":
    asyncio.run(get_miner_data("192.168.1.69"))
```

### Advanced data gathering

If needed, this library exposes a wrapper for the miner API that can be used for advanced data gathering.

#### List available API commands
```python
import asyncio
import sys

from pyasic.miners.miner_factory import MinerFactory

# Fix whatsminer bug
# if the computer is windows, set the event loop policy to a WindowsSelector policy
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def get_api_commands(miner_ip: str):
    # Get the miner
    miner = await MinerFactory().get_miner(miner_ip)
    
    # List all available commands
    print(miner.api.get_commands())
    
    
if __name__ == "__main__":
    asyncio.run(get_api_commands("192.168.1.69"))
```

#### Use miner API commands to gather data

The miner API commands will raise an `APIError` if they fail with a bad status code, to bypass this you must send them manually by using `miner.api.send_command(command, ignore_errors=True)`

```python
import asyncio
import sys

from pyasic.miners.miner_factory import MinerFactory

# Fix whatsminer bug
# if the computer is windows, set the event loop policy to a WindowsSelector policy
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def get_api_commands(miner_ip: str):
    # Get the miner
    miner = await MinerFactory().get_miner(miner_ip)
    
    # Run the devdetails command
    # This is equivalent to await miner.api.send_command("devdetails")
    devdetails: dict = await miner.api.devdetails()
    print(devdetails)
    
    
if __name__ == "__main__":
    asyncio.run(get_api_commands("192.168.1.69"))
```
