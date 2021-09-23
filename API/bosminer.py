from API import BaseMinerAPI


class BOSMinerAPI(BaseMinerAPI):
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
