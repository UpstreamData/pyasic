from API.bosminer import BOSMinerAPI
import asyncio


async def main():
    bosminer = BOSMinerAPI("172.16.1.199")
    data_normal = await bosminer.asccount()
    data_multi = await bosminer.multicommand("version", "config")
    print(data_normal)
    print(data_multi)


asyncio.get_event_loop().run_until_complete(main())
