from API import BaseMinerAPI


class BMMinerAPI(BaseMinerAPI):
    def __init__(self, ip: str, port: int = 4028) -> None:
        super().__init__(ip, port)

    async def version(self) -> dict:
        """
        API 'version' command.

        Returns a dict containing version information.
        """
        return await self.send_command("version")

    async def config(self) -> dict:
        """
        API 'config' command.

        Returns some miner configuration information:
            ASC Count <- the number of ASCs
            PGA Count <- the number of PGAs
            Pool Count <- the number of Pools
            Strategy <- the current pool strategy
            Log Interval <- the interval of logging
            Device Code <- list of compiled device drivers
            OS <- the current operating system
            Failover-Only <- failover-only setting
            Scan Time <- scan-time setting
            Queue <- queue setting
            Expiry <- expiry setting
        """
        return await self.send_command("config")

    async def summary(self) -> dict:
        """API 'summary' command."""
        return await self.send_command("summary")

    async def pools(self) -> dict:
        """API 'pools' command."""
        return await self.send_command("pools")

    async def devs(self) -> dict:
        """API 'devs' command."""
        return await self.send_command("devs")

    async def edevs(self, old: bool = False) -> dict:
        """API 'edevs' command."""
        if old:
            return await self.send_command("edevs", parameters="old")
        else:
            return await self.send_command("edevs")

    async def pga(self, n: int) -> dict:
        """API 'pga' command."""
        return await self.send_command("pga", parameters=n)

    async def pgacount(self) -> dict:
        """API 'pgacount' command."""
        return await self.send_command("pgacount")

    async def switchpool(self, n: int) -> dict:
        """API 'switchpool' command."""
        return await self.send_command("switchpool", parameters=n)

    async def enablepool(self, n: int) -> dict:
        """API 'enablepool' command."""
        return await self.send_command("enablepool", parameters=n)

    async def addpool(self, url: str, username: str, password: str) -> dict:
        """API 'addpool' command."""
        return await self.send_command("addpool", parameters=f"{url}, {username}, {password}")

    async def poolpriority(self, *n: int) -> dict:
        """API 'poolpriority' command."""
        return await self.send_command("poolpriority", parameters=f"{','.join([str(item) for item in n])}")

    async def poolquota(self, n: int, q: int) -> dict:
        """API 'poolquota' command."""
        return await self.send_command("poolquota", parameters=f"{n}, {q}")

    async def disablepool(self, n: int) -> dict:
        """API 'disablepool' command."""
        return await self.send_command("disablepool", parameters=n)

    async def removepool(self, n: int) -> dict:
        """API 'removepool' command."""
        return await self.send_command("removepool", parameters=n)

    async def save(self, filename: str = None) -> dict:
        """API 'save' command."""
        if filename:
            return await self.send_command("save", parameters=filename)
        else:
            return await self.send_command("save")

    async def quit(self) -> dict:
        """quit' command."""
        return await self.send_command("quit")

    async def notify(self) -> dict:
        """API 'notify' command."""
        return await self.send_command("notify")

    async def privileged(self) -> dict:
        """API 'privileged' command."""
        return await self.send_command("privileged")

    async def pgaenable(self, n: int) -> dict:
        """API 'pgaenable' command."""
        return await self.send_command("pgaenable", parameters=n)

    async def pgadisable(self, n: int) -> dict:
        """API 'pgadisable' command."""
        return await self.send_command("pgadisable", parameters=n)

    async def pgaidentify(self, n: int) -> dict:
        """API 'pgaidentify' command."""
        return await self.send_command("pgaidentify", parameters=n)

    async def devdetails(self) -> dict:
        """API 'devdetails' command."""
        return await self.send_command("devdetails")

    async def restart(self) -> dict:
        """API 'restart' command."""
        return await self.send_command("restart")

    async def stats(self) -> dict:
        """API 'stats' command."""
        return await self.send_command("stats")

    async def estats(self, old: bool = False) -> dict:
        """API 'estats' command."""
        if old:
            return await self.send_command("estats", parameters="old")
        else:
            return await self.send_command("estats")

    async def check(self, command) -> dict:
        """API 'check' command."""
        return await self.send_command("check", parameters=command)

    async def failover_only(self, failover: bool) -> dict:
        """API 'failover-only' command."""
        return await self.send_command("failover-only", parameters=failover)

    async def coin(self) -> dict:
        """API 'coin' command."""
        return await self.send_command("coin")

    async def debug(self, setting: str) -> dict:
        """API 'debug' command."""
        return await self.send_command("debug", parameters=setting)

    async def setconfig(self, name: str, n: int) -> dict:
        """API 'setconfig' command."""
        return await self.send_command("setconfig", parameters=f"{name}, {n}")

    async def usbstats(self) -> dict:
        """API 'usbstats' command."""
        return await self.send_command("usbstats")

    async def pgaset(self, n: int, opt: str, val: int = None) -> dict:
        """API 'pgaset' command."""
        if val:
            return await self.send_command("pgaset", parameters=f"{n}, {opt}, {val}")
        else:
            return await self.send_command("pgaset", parameters=f"{n}, {opt}")

    async def zero(self, which: str, value: bool) -> dict:
        """API 'zero' command."""
        return await self.send_command("zero", parameters=f"{which}, {value}")

    async def hotplug(self, n: int) -> dict:
        """API 'hotplug' command."""
        return await self.send_command("hotplug", parameters=n)

    async def asc(self, n: int) -> dict:
        """API 'asc' command."""
        return await self.send_command("asc", parameters=n)

    async def ascenable(self, n: int) -> dict:
        """API 'ascenable' command."""
        return await self.send_command("ascenable", parameters=n)

    async def ascdisable(self, n: int) -> dict:
        """API 'ascdisable' command."""
        return await self.send_command("ascdisable", parameters=n)

    async def ascidentify(self, n: int) -> dict:
        """API 'ascidentify' command."""
        return await self.send_command("ascidentify", parameters=n)

    async def asccount(self) -> dict:
        """API 'asccount' command."""
        return await self.send_command("asccount")

    async def ascset(self, n: int, opt: str, val: int = None) -> dict:
        """API 'ascset' command."""
        if val:
            return await self.send_command("ascset", parameters=f"{n}, {opt}, {val}")
        else:
            return await self.send_command("ascset", parameters=f"{n}, {opt}")

    async def lcd(self) -> dict:
        """API 'lcd' command."""
        return await self.send_command("lcd")

    async def lockstats(self) -> dict:
        """API 'lockstats' command."""
        return await self.send_command("lockstats")
