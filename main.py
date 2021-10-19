from network import MinerNetwork
from miners.bosminer import BOSminer
import asyncio


async def main():
    miner_network = MinerNetwork('192.168.1.1')
    miners = await miner_network.scan_network_for_miners()
    # print("\n".join([str(miner.ip) for miner in miners]))
    good_list = list(filter(None, await asyncio.gather(*[miner.check_good_boards() for miner in miners])))
    print("\n".join(good_list))
    print(len(good_list))
    # print('\n'.join([f"{str(miner.ip)}" for miner in miners]))

async def main_bad():
    miner_network = MinerNetwork('192.168.1.1')
    miners = await miner_network.scan_network_for_miners()
    bad_list = list(filter(None, await asyncio.gather(*[miner.get_bad_boards() for miner in miners])))
    print(bad_list)
    print(len(bad_list))

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
