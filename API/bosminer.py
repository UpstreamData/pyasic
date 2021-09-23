from API import BaseMinerAPI


class BOSMinerAPI(BaseMinerAPI):
    def __init__(self, ip, port=4028):
        super().__init__(ip, port)

    async def asccount(self):
        return await self.send_command("asccount")

    async def asc(self, n: int):
        return await self.send_command("asc", parameters=n)

    async def devdetails(self):
        return await self.send_command("devdetails")

    async def devs(self):
        return await self.send_command("devs")

    async def edevs(self, old: bool = False):
        if old:
            return await self.send_command("edevs", parameters="old")
        else:
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

    async def switchpool(self, n: int):
        return await self.send_command("switchpool", parameters=n)

    async def enablepool(self, n: int):
        return await self.send_command("enablepool", parameters=n)

    async def disablepool(self, n: int):
        return await self.send_command("disablepool", parameters=n)

    async def addpool(self, url: str, username: str, password: str):
        return await self.send_command("addpool", parameters=f"{url}, {username}, {password}")

    async def removepool(self, n: int):
        return await self.send_command("removepool", parameters=n)

    async def fans(self):
        return await self.send_command("fans")

    async def tempctrl(self):
        return await self.send_command("tempctrl")

    async def temps(self):
        return await self.send_command("temps")

    async def tunerstatus(self):
        return await self.send_command("tunerstatus")

    async def pause(self):
        return await self.send_command("pause")

    async def resume(self):
        return await self.send_command("resume")