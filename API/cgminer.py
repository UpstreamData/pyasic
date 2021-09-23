from API import BaseMinerAPI


class CGMinerAPI(BaseMinerAPI):
    def __init__(self, ip, port=4028):
        super().__init__(ip, port)

    async def version(self):
        return await self.send_command("version")

    async def summary(self):
        return await self.send_command("summary")

    async def pools(self):
        return await self.send_command("pools")

    async def devs(self):
        return await self.send_command("devs")

    async def edevs(self, old: bool = False):
        if old:
            return await self.send_command("edevs", parameters="old")
        else:
            return await self.send_command("edevs")

    async def pga(self, n: int):
        return await self.send_command("pga", parameters=n)

    async def pgacount(self):
        return await self.send_command("pgacount")

    async def switchpool(self, n: int):
        return await self.send_command("switchpool", parameters=n)

    async def enablepool(self, n: int):
        return await self.send_command("enablepool", parameters=n)

    async def addpool(self, url: str, username: str, password: str):
        return await self.send_command("addpool", parameters=f"{url}, {username}, {password}")

    async def poolpriority(self, *n: int):
        return await self.send_command("poolpriority", parameters=f"{','.join(n)}")

    async def poolquota(self, n: int, q: int):
        return await self.send_command("poolquota", parameters=f"{n}, {q}")

    async def disablepool(self, n: int):
        return await self.send_command("disablepool", parameters=n)

    async def removepool(self, n: int):
        return await self.send_command("removepool", parameters=n)

    async def save(self, filename: str = None):
        if filename:
            return await self.send_command("save", parameters=filename)
        else:
            return await self.send_command("save")

    async def quit(self):
        return await self.send_command("quit")

    async def notify(self):
        return await self.send_command("notify")

    async def privileged(self):
        return await self.send_command("privileged")

    async def pgaenable(self, n: int):
        return await self.send_command("pgaenable", parameters=n)

    async def pgadisable(self, n: int):
        return await self.send_command("pgadisable", parameters=n)

    async def pgaidentify(self, n: int):
        return await self.send_command("pgaidentify", parameters=n)

    async def devdetails(self):
        return await self.send_command("devdetails")

    async def restart(self):
        return await self.send_command("restart")

    async def stats(self):
        return await self.send_command("stats")

    async def estats(self, old: bool = False):
        if old:
            return await self.send_command("estats", parameters="old")
        else:
            return await self.send_command("estats")

    async def check(self, command):
        return await self.send_command("check", parameters=command)

    async def failover_only(self, failover: bool):
        return self.send_command("failover-only", parameters=failover)

    async def coin(self):
        return await self.send_command("coin")

    async def debug(self, setting: str):
        return await self.send_command("debug", parameters=setting)

    async def setconfig(self, name: str, n: int):
        return await self.send_command("setconfig", parameters=f"{name}, {n}")

    async def usbstats(self):
        return await self.send_command("usbstats")

    async def pgaset(self, n: int, opt: str, val: int = None):
        if val:
            return await self.send_command("pgaset", parameters=f"{n}, {opt}, {val}")
        else:
            return await self.send_command("pgaset", parameters=f"{n}, {opt}")

    async def zero(self, which: str, value: bool):
        return await self.send_command("zero", parameters=f"{which}, {value}")

    async def hotplug(self, n: int):
        return await self.send_command("hotplug", parameters=n)

    async def asc(self, n: int):
        return await self.send_command("asc", parameters=n)

    async def ascenable(self, n: int):
        return await self.send_command("ascenable", parameters=n)

    async def ascdisable(self, n: int):
        return await self.send_command("ascdisable", parameters=n)

    async def ascidentify(self, n: int):
        return await self.send_command("ascidentify", parameters=n)

    async def asccount(self):
        return await self.send_command("asccount")

    async def ascset(self, n: int, opt: str, val: int = None):
        if val:
            return await self.send_command("ascset", parameters=f"{n}, {opt}, {val}")
        else:
            return await self.send_command("ascset", parameters=f"{n}, {opt}")

    async def lcd(self):
        return await self.send_command("lcd")

    async def lockstats(self):
        return await self.send_command("lockstats")
