import asyncio

from pyasic import get_miner
import json
import datetime

async def main():
    ip = '10.7.11.101'
    try:
        miner = await get_miner(ip)
        data = await miner.get_data()


        print(data)

        # def custom_serializer(o):
        #     if isinstance(o, datetime.datetime):
        #         return o.isoformat()
        #     try:
        #         return o.__dict__
        #     except AttributeError:
        #         return str(o)
        #
        # print(json.dumps(data, default=custom_serializer, indent=4))
    except Exception as e:
        print(f"Error:: {e}")

if __name__ == "__main__":
    asyncio.run(main())