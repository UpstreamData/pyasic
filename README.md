# minerInterface
*A set of modules for interfacing with many common types of ASIC bitcoin miners, using both their API and SSH.*
## Usage
To use this repo, first download it, create a virtual environment, enter the virtual environment, and install relevant packages by navigating to this directory and running ```pip install -r requirements.txt``` on Windows or ```pip3 install -r requirements.txt``` on Mac or UNIX if the first command fails.

### CFG Util
*CFG Util is a GUI for interfacing with the miners easily, it is mostly self-explanatory.*

To use CFG Util you have 2 options -
1. Run it directly with the file ```config_tool.py``` or import it with ```from cfg_util import main```, then run the ```main()``` function in an asyncio event loop like -

```python
from cfg_util import main

if __name__ == '__main__':
    main()
```
2. Make a build of the CFG Util for your system using cx_freeze and ```make_cfg_tool_exe.py```
   1. Open either Command Prompt on Windows or Terminal on Mac or UNIX.
   2. Navigate to this directory, and run ```make_cfg_tool_exe.py build``` on Windows or ```python3 make_cfg_tool_exe.py``` on Mac or UNIX.

### Interfacing with miners programmatically

To write your own custom programs with this repo, you have many options.

It is recommended that you explore the files in this repo to familiarize yourself with them, try starting with the miners module and going from there.

A basic script to find all miners on the network and get the hashrate from them looks like this -

```python
import asyncio
from network import MinerNetwork
from cfg_util.func import safe_parse_api_data

async def get_hashrate():
    # Miner Network class allows for easy scanning of a network
    # Give it any IP on a network and it will find the whole subnet
    # It can also be passed a subnet mask:
        # miner_network = MinerNetwork('192.168.1.55', mask=23)
    miner_network = MinerNetwork('192.168.1.1')
    # Miner Network scan function returns Miner classes for all miners found
    miners = await miner_network.scan_network_for_miners()
    # Each miner will return with its own set of functions, and an API class instance
    tasks = [miner.api.summary() for miner in miners]
    # Gather all tasks asynchronously and run them
    data = await asyncio.gather(*tasks)
    parse_tasks = []
    for item in data:
        # safe_parse_api_data parses the data from a miner API
        # It will raise an APIError (from API import APIError) if there is a problem
        parse_tasks.append(safe_parse_api_data(item, 'SUMMARY', 0, 'MHS 5s'))
    # Gather all tasks asynchronously and run them
    data = await asyncio.gather(*parse_tasks)
    # Print a list of all the hashrates
    print(data)

if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(get_hashrate())
```
<br>
You can also create your own miner without scanning if you know the IP:

```python
import asyncio
import ipaddress
from miners.miner_factory import MinerFactory
from cfg_util.func import safe_parse_api_data

async def get_miner_hashrate(ip: str):
    # Instantiate a Miner Factory to generate miners from their IP
    miner_factory = MinerFactory()
    # Make the string IP into an IP address
    miner_ip = ipaddress.ip_address(ip)
    # Wait for the factory to return the miner
    miner = await miner_factory.get_miner(miner_ip)
    # Get the API data
    summary = await miner.api.summary()
    # safe_parse_api_data parses the data from a miner API
    # It will raise an APIError (from API import APIError) if there is a problem
    data = await safe_parse_api_data(summary, 'SUMMARY', 0, 'MHS 5s')
    print(data)

if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(get_miner_hashrate(str("192.168.1.69")))
```

<br>
Or generate a miner directly without the factory:

```python
import asyncio
from miners.bosminer import BOSminer
from cfg_util.func import safe_parse_api_data

async def get_miner_hashrate(ip: str):
    # Create a BOSminer miner object
    miner = BOSminer(ip)
    # Get the API data
    summary = await miner.api.summary()
    # safe_parse_api_data parses the data from a miner API
    # It will raise an APIError (from API import APIError) if there is a problem
    data = await safe_parse_api_data(summary, 'SUMMARY', 0, 'MHS 5s')
    print(data)

if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(get_miner_hashrate(str("192.168.1.69")))
```

<br>
Or finally, just get the API directly:

```python
import asyncio
from API.bosminer import BOSMinerAPI
from cfg_util.func import safe_parse_api_data

async def get_miner_hashrate(ip: str):
    # Create a BOSminerAPI object
    # Port can be declared manually, if not it defaults to 4028
    api = BOSMinerAPI(ip, port=4028)
    # Get the API data
    summary = await api.summary()
    # safe_parse_api_data parses the data from a miner API
    # It will raise an APIError (from API import APIError) if there is a problem
    data = await safe_parse_api_data(summary, 'SUMMARY', 0, 'MHS 5s')
    print(data)

if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(get_miner_hashrate(str("192.168.1.69")))
```
