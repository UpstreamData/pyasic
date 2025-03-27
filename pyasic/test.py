import asyncio

from pyasic import get_miner
import json
import datetime

async def main():
    ip = '10.2.110.188'
    try:
        miner = await get_miner(ip)
        update_pwd = await miner.update_pwd(cur_pwd="root", new_pwd="admin")

        if update_pwd:
            print("update_pwd is true")
        else:
            print("update_pwd is false")

        # data = await miner.get_data()
        #
        #
        # print(data)

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