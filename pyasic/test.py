import asyncio

from pyasic import get_miner, settings
import json
import datetime

async def main():
    ip = '10.2.108.10'
    try:
        # cur_pwd = "root"
        # new_pwd = "admin"
        settings.update("default_antminer_web_password", "admin")
        miner = await get_miner(ip=ip)
        # update_pwd = await miner.update_pwd(cur_pwd=cur_pwd, new_pwd=new_pwd)
        #
        # if update_pwd:
        #     print("update_pwd is true")
        # else:
        #     print("update_pwd is false")

        data = await miner.get_data()


        # print(data)

        def custom_serializer(o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()
            try:
                return o.__dict__
            except AttributeError:
                return str(o)

        print(json.dumps(data, default=custom_serializer, indent=4))
    except Exception as e:
        print(f"Error:: {e}")

if __name__ == "__main__":
    asyncio.run(main())