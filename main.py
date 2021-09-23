import asyncio
import json


class APIError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"{self.message}"
        else:
            return "Incorrect API parameters."


class API:
    def __init__(self, ip, port):
        self.port = port
        self.ip = ip

    async def send_command(self, command):
        # get reader and writer streams
        reader, writer = await asyncio.open_connection(self.ip, self.port)

        # send the command
        writer.write(json.dumps({"command": command}).encode('utf-8'))
        await writer.drain()

        # instantiate data
        data = b""

        # loop to receive all the data
        while True:
            d = await reader.read(4096)
            if not d:
                break
            data += d

        data = json.loads(data.decode('utf-8')[:-1])

        # close the connection
        writer.close()
        await writer.wait_closed()

        # check if the data returned is correct or an error
        if not data["STATUS"][0]["STATUS"] == "S":
            # this is an error
            raise APIError(data["STATUS"][0]["Msg"])

        # return the data
        return data


class CGMiner(API):
    def __init__(self, ip, port=4028):
        super().__init__(ip, port)


class BMMiner(API):
    def __init__(self, ip, port=4028):
        super().__init__(ip, port)

    async def version(self):
        return await self.send_command("version")

    async def config(self):
        return await self.send_command("config")

    async def summary(self):
        return await self.send_command("summary")

    async def pools(self):
        return await self.send_command("pools")

    async def devs(self):
        return await self.send_command("devs")

    async def edevs(self):
        return await self.send_command("edevs")

    async def pgacount(self):
        return await self.send_command("pgacount")

    async def notify(self):
        return await self.send_command("notify")

    async def devdetails(self):
        return await self.send_command("devdetails")

    async def stats(self):
        return await self.send_command("stats")

    async def estats(self):
        return await self.send_command("estats")

    async def check(self):
        return await self.send_command("check")

    async def coin(self):
        return await self.send_command("coin")

    async def asccount(self):
        return await self.send_command("asccount")

    async def lcd(self):
        return await self.send_command("lcd")


class BOSMiner(API):
    def __init__(self, ip, port=4028):
        super().__init__(ip, port)

    async def asccount(self):
        return await self.send_command("asccount")

    async def devdetails(self):
        return await self.send_command("devdetails")

    async def devs(self):
        return await self.send_command("devs")

    async def edevs(self):
        return await self.send_command("edevs")

    async def pools(self):
        return await self.send_command("pools")

    async def summary(self):
        return await self.send_command("summary")

    async def stats(self):
        return await self.send_command("stats")

    async def version(self):
        return await self.send_command("version")

    async def estats(self):
        return await self.send_command("estats")

    async def check(self):
        return await self.send_command("check")

    async def coin(self):
        return await self.send_command("coin")

    async def lcd(self):
        return await self.send_command("lcd")

    async def fans(self):
        return await self.send_command("fans")

    async def tempctrl(self):
        return await self.send_command("tempctrl")

    async def temps(self):
        return await self.send_command("temps")

    async def tunerstatus(self):
        return await self.send_command("tunerstatus")


async def main():
    bosminer = BOSMiner("172.16.1.199")
    data = await bosminer.stats()
    print(data)


asyncio.get_event_loop().run_until_complete(main())
