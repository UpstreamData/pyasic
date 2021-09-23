from API.bosminer import BOSMinerAPI
import asyncio


async def main():
    bosminer = BOSMinerAPI("172.16.1.199")
    data = await bosminer.stats()
    print(data)


asyncio.get_event_loop().run_until_complete(main())
