from network import MinerNetwork
from miners.bosminer import BOSminer
import asyncio
from API.bosminer import BOSMinerAPI
from API.cgminer import CGMinerAPI
import sys
from cfg_util.func.data import safe_parse_api_data


# Fix bug with some whatsminers and asyncio because of a socket not being shut down:
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def good_boards():
    miner_network = MinerNetwork('192.168.1.1')
    miners = await miner_network.scan_network_for_miners()
    # print("\n".join([str(miner.ip) for miner in miners]))
    good_list = list(filter(None, await asyncio.gather(*[miner.check_good_boards() for miner in miners])))
    print("\n".join(good_list))
    print(len(good_list))
    # print('\n'.join([f"{str(miner.ip)}" for miner in miners]))


async def bad_boards():
    miner_network = MinerNetwork('192.168.1.1')
    miners = await miner_network.scan_network_for_miners()
    bad_list = list(filter(None, await asyncio.gather(*[miner.get_bad_boards() for miner in miners if isinstance(miner, BOSminer)])))
    print(bad_list)
    print(len(bad_list))


async def braiins_update():
    miners = [BOSminer('192.168.1.36')]
    cmd = "wget -O /tmp/firmware.tar https://feeds.braiins-os.com/am1-s9/firmware_2021-10-27-0-a6497b86-21.09.3-plus_arm_cortex-a9_neon.tar && sysupgrade /tmp/firmware.tar"
    tasks = []
    for miner in miners:
        if isinstance(miner, BOSminer):
            tasks.append(miner.send_ssh_command(cmd))
    results = await asyncio.gather(*tasks)
    print(results)


async def test_command():
    miner_network = MinerNetwork('192.168.1.1')
    miners = await miner_network.scan_network_for_miners()
    tasks = [miner.api.summary() for miner in miners]
    data = await asyncio.gather(*tasks)
    parse_tasks = []
    for item in data:
        parse_tasks.append(safe_parse_api_data(item, 'SUMMARY', 0, 'MHS 5s'))
    data = await asyncio.gather(*parse_tasks)
    print(data)

async def get_commands_from_miner_api():
    miner = BOSMinerAPI("192.168.1.1")
    print(miner.get_commands())
    miner = CGMinerAPI("192.168.1.1")
    print(miner.get_commands())


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(test_command())
