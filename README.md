# minerInterface
*A set of modules for interfacing with many common types of ASIC bitcoin miners, using both their API and SSH.*
## Usage
To use this repo, first download it, create a virtual environment, enter the virtual environment, and install relevant packages by navigating to this directory and running ```pip install -r requirements.txt``` on Windows or ```pip3 install -r requirements.txt``` on Mac or UNIX if the first command fails.

For those of you who aren't comfortable with code and developer tools, there are windows builds of the GUI applications here -> (https://drive.google.com/drive/folders/1DjR8UOS_g0ehfiJcgmrV0FFoqFvE9akW?usp=sharing)

### CFG Util
*CFG Util is a GUI for interfacing with the miners easily, it is mostly self-explanatory.*

To use CFG Util you have 2 options -
1. Run it directly with the file ```config_tool.py``` or import it with ```from cfg_util import main```, then run the ```main()``` function like -

```python
from tools.cfg_util import main

if __name__ == '__main__':
    main()
```
2. Make a build of the CFG Util for your system using cx_freeze and ```make_cfg_tool_exe.py```
(Alternatively, you can get a build made by me here -> https://drive.google.com/drive/folders/147vBXbuaX85inataXeSAiKk8IKf-7xtR)
   1. Open either Command Prompt on Windows or Terminal on Mac or UNIX.
   2. Navigate to this directory, and run ```make_cfg_tool_exe.py build``` on Windows or ```python3 make_cfg_tool_exe.py build``` on Mac or UNIX.

### Interfacing with miners programmatically
<br>

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

A basic script to find all miners on the network and get the hashrate from them looks like this -

```python
import asyncio
from network import MinerNetwork


async def get_hashrate():
    # Miner Network class allows for easy scanning of a network
    # Give it any IP on a network and it will find the whole subnet
    # It can also be passed a subnet mask:
    # miner_network = MinerNetwork('192.168.1.55', mask=23)
    miner_network = MinerNetwork('192.168.1.1')
    # Miner Network scan function returns Miner classes for all miners found
    miners = await miner_network.scan_network_for_miners()
    # Each miner will return with its own set of functions, and an API class instance
    tasks = [miner.get_data() for miner in miners]
    # Gather all tasks asynchronously and run them
    data = await asyncio.gather(*tasks)
    # now we have a list of MinerData, and can get .hashrate
    print([item.hashrate for item in data])


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(get_hashrate())
```
<br>
You can also create your own miner without scanning if you know the IP:

```python
import asyncio
import ipaddress
from miners.miner_factory import MinerFactory



async def get_miner_hashrate(ip: str):
    # Instantiate a Miner Factory to generate miners from their IP
    miner_factory = MinerFactory()
    # Make the string IP into an IP address
    miner_ip = ipaddress.ip_address(ip)
    # Wait for the factory to return the miner
    miner = await miner_factory.get_miner(miner_ip)
    # Get the API data
    data = await miner.get_data()
    # print out hashrate
    print(data.hashrate)


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(
        get_miner_hashrate(str("192.168.1.69")))
```


Now that you know that, lets move on to some common API functions that you might want to use.

### Common commands:
* Get the data used by the config utility, this includes pool data, wattage use, temperature, hashrate, etc:
* All the data from below commands and more are returned from this in a consistent dataclass.  Check out the `MinerData` class in  `/data/__init__.py` for more information.

```python
import asyncio
import ipaddress
from miners.miner_factory import MinerFactory


async def get_miner_pool_data(ip: str):
    # Instantiate a Miner Factory to generate miners from their IP
    miner_factory = MinerFactory()
    # Make the string IP into an IP address
    miner_ip = ipaddress.ip_address(ip)
    # Wait for the factory to return the miner
    miner = await miner_factory.get_miner(miner_ip)
    # Get the data
    data = await miner.get_data()
    
    print(data)


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(
        get_miner_pool_data(str("192.168.1.69")))
```



* Getting pool data:

```python
import asyncio
import ipaddress
from miners.miner_factory import MinerFactory


async def get_miner_pool_data(ip: str):
    # Instantiate a Miner Factory to generate miners from their IP
    miner_factory = MinerFactory()
    # Make the string IP into an IP address
    miner_ip = ipaddress.ip_address(ip)
    # Wait for the factory to return the miner
    miner = await miner_factory.get_miner(miner_ip)
    # Get the API data
    pools = await miner.api.pools()
    # safe_parse_api_data parses the data from a miner API
    # It will raise an APIError (from API import APIError) if there is a problem
    data = pools["POOLS"]
    # parse further from here to get all the pool info you want.
    # each pool is on a different index eg:
    # data[0] is pool 1
    # data[1] is pool 2
    # etc
    print(data)


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(
        get_miner_pool_data(str("192.168.1.69")))
```

* Getting temperature data:

This one is a bit tougher, lots of miners do this a different way, you might need to experiment a bit to find what works for you.
BraiinsOS uses the "temps" command, Whatsminers has it in "devs", Avalonminers put it in "stats" as well as some other miners,
but the spot I like to try first is in "summary".

A pretty good example of really trying to make this robust is in ```cfg_util.func.miners``` in the ```get_formatted_data()``` function.

```python
import asyncio
import ipaddress
from miners.miner_factory import MinerFactory


async def get_miner_temperature_data(ip: str):
    # Instantiate a Miner Factory to generate miners from their IP
    miner_factory = MinerFactory()
    # Make the string IP into an IP address
    miner_ip = ipaddress.ip_address(ip)
    # Wait for the factory to return the miner
    miner = await miner_factory.get_miner(miner_ip)
    # Get the API data
    summary = await miner.api.summary()

    data = summary['SUMMARY'][0]["Temperature"]
    print(data)


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(
        get_miner_temperature_data(str("192.168.1.69")))
```

* Getting power data:

How about data on the power usage of the miner?  This one only works for Whatsminers and BraiinsOS for now, and the Braiins one just uses the tuning setting, but its good enough for basic uses.

```python
import asyncio
import ipaddress
from miners.miner_factory import MinerFactory


async def get_miner_power_data(ip: str):
    data = None
    # Instantiate a Miner Factory to generate miners from their IP
    miner_factory = MinerFactory()
    # Make the string IP into an IP address
    miner_ip = ipaddress.ip_address(ip)
    # Wait for the factory to return the miner
    miner = await miner_factory.get_miner(miner_ip)
    # check if this can be sent the "tunerstatus" command, BraiinsOS only
    if "tunerstatus" in miner.api.get_commands():
        # send the command
        tunerstatus = await miner.api.tunerstatus()
        # parse the return
        data = tunerstatus['TUNERSTATUS'][0]["PowerLimit"]
    else:
        # send the command
        # whatsminers have the power info in summary
        summary = await miner.api.summary()
        # parse the return
        data = summary['SUMMARY'][0]["Power"]

    if data:
       print(data)


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(
        get_miner_power_data(str("192.168.1.69")))
```

* Multicommands:

Multicommands make it much easier to get many types of data all at once.  The multicommand function will also remove any commands that your API can't handle automatically.
How about we get the current pool user and hashrate in 1 command?

```python
import asyncio
import ipaddress
from miners.miner_factory import MinerFactory
from tools.cfg_util_old.func.parse_data import safe_parse_api_data


async def get_miner_hashrate_and_pool(ip: str):
    # Instantiate a Miner Factory to generate miners from their IP
    miner_factory = MinerFactory()
    # Make the string IP into an IP address
    miner_ip = ipaddress.ip_address(ip)
    # Wait for the factory to return the miner
    miner = await miner_factory.get_miner(miner_ip)
    # Get the API data
    api_data = await miner.api.multicommand("pools", "summary")
    if "pools" in api_data.keys():
        user = api_data["pools"][0]["POOLS"][0]["User"]
        print(user)
    if "summary" in api_data.keys():
        hashrate = api_data["summary"][0]["SUMMARY"][0]["MHS av"]
        print(hashrate)


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(
        get_miner_hashrate_and_pool(str("192.168.1.9")))
```
