import asyncio
import datetime
import json

from pyasic import get_miner


async def main():
    ip = "10.9.190.2"
    try:

        # settings.update("default_antminer_web_password", "admin")

        miner = await get_miner(ip=ip)

        print(f"Miner: {miner}")


        # resume = await miner.resume_mining()
        # print(f"Resume mining: {resume}")

        # stop = await miner.stop_mining()
        # print(f"Stop mining: {stop}")

        errors = await miner.get_errors()

        dataMiner = await miner.get_data()
        Hashboards = await miner.get_hashboards()

        miningMode = await miner.is_mining()
        sleepMode = await miner.is_sleep()

        # print(f"Hashboards: {Hashboards}")
        # print(f"Miner : {dataMiner}")
        print(f"Errors: {errors}")
        print(f"Is mining: {miningMode}")
        print(f"Sleep mode:  {sleepMode}")

        # Перевод в сон
        try:
            goSleep = await miner.stop_mining()
            print(f"GoSleep: {goSleep}")
        except Exception as e:
            print(f"GoSleep Error: {e}")

        # Вывод из сна
        # try:
        #     goResume = await miner.resume_mining()
        #     print(f"GoResume: {goResume}")
        # except Exception as e:
        #     print(f"GoResume: Error {e}")




        # cur_pwd = "root"
        # new_pwd = "admin"
        # settings.update("default_antminer_web_password", "admin")

        # update_pwd = await miner.update_pwd(cur_pwd=cur_pwd, new_pwd=new_pwd)
        #
        # if update_pwd:
        #     print("update_pwd is true")
        # else:
        #     print("update_pwd is false")

        # try:
        #     data = await miner.resume_mining()
        # except Exception as e:
        #     print(e)

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
