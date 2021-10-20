from API import BaseMinerAPI


class CGMinerAPI(BaseMinerAPI):
    def __init__(self, ip, port=4028):
        super().__init__(ip, port)

    async def version(self) -> dict:
        return await self.send_command("version")

    async def summary(self) -> dict:
        return await self.send_command("summary")

    async def pools(self) -> dict:
        return await self.send_command("pools")

    async def devs(self) -> dict:
        return await self.send_command("devs")

    async def edevs(self, old: bool = False) -> dict:
        if old:
            return await self.send_command("edevs", parameters="old")
        else:
            return await self.send_command("edevs")

    async def pga(self, n: int) -> dict:
        return await self.send_command("pga", parameters=n)

    async def pgacount(self) -> dict:
        return await self.send_command("pgacount")

    async def switchpool(self, n: int) -> dict:
        return await self.send_command("switchpool", parameters=n)

    async def enablepool(self, n: int) -> dict:
        return await self.send_command("enablepool", parameters=n)

    async def addpool(self, url: str, username: str, password: str) -> dict:
        return await self.send_command("addpool", parameters=f"{url}, {username}, {password}")

    async def poolpriority(self, *n: int) -> dict:
        return await self.send_command("poolpriority", parameters=f"{','.join([str(item) for item in n])}")

    async def poolquota(self, n: int, q: int) -> dict:
        return await self.send_command("poolquota", parameters=f"{n}, {q}")

    async def disablepool(self, n: int) -> dict:
        return await self.send_command("disablepool", parameters=n)

    async def removepool(self, n: int) -> dict:
        return await self.send_command("removepool", parameters=n)

    async def save(self, filename: str = None) -> dict:
        if filename:
            return await self.send_command("save", parameters=filename)
        else:
            return await self.send_command("save")

    async def quit(self) -> dict:
        return await self.send_command("quit")

    async def notify(self) -> dict:
        return await self.send_command("notify")

    async def privileged(self) -> dict:
        return await self.send_command("privileged")

    async def pgaenable(self, n: int) -> dict:
        return await self.send_command("pgaenable", parameters=n)

    async def pgadisable(self, n: int) -> dict:
        return await self.send_command("pgadisable", parameters=n)

    async def pgaidentify(self, n: int) -> dict:
        return await self.send_command("pgaidentify", parameters=n)

    async def devdetails(self) -> dict:
        return await self.send_command("devdetails")

    async def restart(self) -> dict:
        return await self.send_command("restart")

    async def stats(self) -> dict:
        return await self.send_command("stats")

    async def estats(self, old: bool = False) -> dict:
        if old:
            return await self.send_command("estats", parameters="old")
        else:
            return await self.send_command("estats")

    async def check(self, command) -> dict:
        return await self.send_command("check", parameters=command)

    async def failover_only(self, failover: bool) -> dict:
        return await self.send_command("failover-only", parameters=failover)

    async def coin(self) -> dict:
        return await self.send_command("coin")

    async def debug(self, setting: str) -> dict:
        return await self.send_command("debug", parameters=setting)

    async def setconfig(self, name: str, n: int) -> dict:
        return await self.send_command("setconfig", parameters=f"{name}, {n}")

    async def usbstats(self) -> dict:
        return await self.send_command("usbstats")

    async def pgaset(self, n: int, opt: str, val: int = None) -> dict:
        if val:
            return await self.send_command("pgaset", parameters=f"{n}, {opt}, {val}")
        else:
            return await self.send_command("pgaset", parameters=f"{n}, {opt}")

    async def zero(self, which: str, value: bool) -> dict:
        return await self.send_command("zero", parameters=f"{which}, {value}")

    async def hotplug(self, n: int) -> dict:
        return await self.send_command("hotplug", parameters=n)

    async def asc(self, n: int) -> dict:
        return await self.send_command("asc", parameters=n)

    async def ascenable(self, n: int) -> dict:
        return await self.send_command("ascenable", parameters=n)

    async def ascdisable(self, n: int) -> dict:
        return await self.send_command("ascdisable", parameters=n)

    async def ascidentify(self, n: int) -> dict:
        return await self.send_command("ascidentify", parameters=n)

    async def asccount(self) -> dict:
        return await self.send_command("asccount")

    async def ascset(self, n: int, opt: str, val: int = None) -> dict:
        if val:
            return await self.send_command("ascset", parameters=f"{n}, {opt}, {val}")
        else:
            return await self.send_command("ascset", parameters=f"{n}, {opt}")

    async def lcd(self) -> dict:
        return await self.send_command("lcd")

    async def lockstats(self) -> dict:
        return await self.send_command("lockstats")
