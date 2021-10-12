from network import MinerNetwork
from miners.bosminer import BOSminer
import asyncio


async def main():
    miner_network = MinerNetwork('192.168.1.1')
    data = await miner_network.scan_network_for_miners()
    config = await asyncio.gather(*[miner.get_config() for miner in data if isinstance(miner, BOSminer)])
    print(config)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
