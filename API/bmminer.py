from API import BaseMinerAPI


class BMMinerAPI(BaseMinerAPI):
    """
    A class that abstracts the BMMiner API in the miners.

    Each method corresponds to an API command in BMMiner.

    BMMiner API documentation:
        https://github.com/jameshilliard/bmminer/blob/master/API-README

    Parameters:
        ip: the IP address of the miner.
        port (optional): the port of the API on the miner (standard is 4028)
    """
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
        """
        API 'summary' command.

        Returns a dict containing the status summary of the miner.
        """
        return await self.send_command("summary")

    async def pools(self) -> dict:
        """
        API 'pools' command.

        Returns a dict containing the status of each pool.
        """
        return await self.send_command("pools")

    async def devs(self) -> dict:
        """
        API 'devs' command.

        Returns a dict containing each PGA/ASC with their details.
        """
        return await self.send_command("devs")

    async def edevs(self, old: bool = False) -> dict:
        """
        API 'edevs' command.

        Returns a dict containing each PGA/ASC with their details,
        ignoring blacklisted devices and zombie devices.

        Parameters:
            old (optional): include zombie devices that became zombies less than 'old' seconds ago
        """
        if old:
            return await self.send_command("edevs", parameters="old")
        else:
            return await self.send_command("edevs")

    async def pga(self, n: int) -> dict:
        """
        API 'pga' command.

        Returns a dict containing the details of a single PGA of number N.

        Parameters:
            n: the number of the PGA to get details of.
        """
        return await self.send_command("pga", parameters=n)

    async def pgacount(self) -> dict:
        """
        API 'pgacount' command.

        Returns a dict containing the number of PGA devices.
        """
        return await self.send_command("pgacount")

    async def switchpool(self, n: int) -> dict:
        """
        API 'switchpool' command.

        Returns the STATUS section with the results of switching pools.

        Parameters:
            n: the number of the pool to switch to.
        """
        return await self.send_command("switchpool", parameters=n)

    async def enablepool(self, n: int) -> dict:
        """
        API 'enablepool' command.

        Returns the STATUS section with the results of enabling the pool.

        Parameters:
            n: the number of the pool to enable.
        """
        return await self.send_command("enablepool", parameters=n)

    async def addpool(self, url: str, username: str, password: str) -> dict:
        """
        API 'addpool' command.

        Returns the STATUS section with the results of adding the pool.

        Parameters:
            url: the URL of the new pool to add.
            username: the users username on the new pool.
            password: the worker password on the new pool.
        """
        return await self.send_command("addpool", parameters=f"{url}, {username}, {password}")

    async def poolpriority(self, *n: int) -> dict:
        """
        API 'poolpriority' command.

        Returns the STATUS section with the results of setting pool priority.

        Parameters:
            n: pool numbers in order of priority.
        """
        return await self.send_command("poolpriority", parameters=f"{','.join([str(item) for item in n])}")

    async def poolquota(self, n: int, q: int) -> dict:
        """
        API 'poolquota' command.

        Returns the STATUS section with the results of setting pool quota.

        Parameters:
            n: pool number to set quota on.
            q: quota to set the pool to.
        """
        return await self.send_command("poolquota", parameters=f"{n}, {q}")

    async def disablepool(self, n: int) -> dict:
        """
        API 'disablepool' command.

        Returns the STATUS section with the results of disabling the pool.

        Parameters:
            n: the number of the pool to disable.
        """
        return await self.send_command("disablepool", parameters=n)

    async def removepool(self, n: int) -> dict:
        """
        API 'removepool' command.

        Returns the STATUS section with the results of removing the pool.

        Parameters:
            n: the number of the pool to remove.
        """
        return await self.send_command("removepool", parameters=n)

    async def save(self, filename: str = None) -> dict:
        """
        API 'save' command.

        Returns the STATUS section with the results of saving the config file..

        Parameters:
            filename (optional): the filename to save the config as.
        """
        if filename:
            return await self.send_command("save", parameters=filename)
        else:
            return await self.send_command("save")

    async def quit(self) -> dict:
        """
        API 'quit' command.

        Returns a single "BYE" before BMMiner quits.
        """
        return await self.send_command("quit")

    async def notify(self) -> dict:
        """
        API 'notify' command.

        Returns a dict containing the last status and count of each devices problem(s).
        """
        return await self.send_command("notify")

    async def privileged(self) -> dict:
        """
        API 'privileged' command.

        Returns the STATUS section with an error if you have no privileged access.
        """
        return await self.send_command("privileged")

    async def pgaenable(self, n: int) -> dict:
        """
        API 'pgaenable' command.

        Returns the STATUS section with the results of enabling the PGA device N.

        Parameters:
            n: the number of the PGA to enable.
        """
        return await self.send_command("pgaenable", parameters=n)

    async def pgadisable(self, n: int) -> dict:
        """
        API 'pgadisable' command.

        Returns the STATUS section with the results of disabling the PGA device N.

        Parameters:
            n: the number of the PGA to disable.
        """
        return await self.send_command("pgadisable", parameters=n)

    async def pgaidentify(self, n: int) -> dict:
        """
        API 'pgaidentify' command.

        Returns the STATUS section with the results of identifying the PGA device N.

        Parameters:
            n: the number of the PGA to identify.
        """
        return await self.send_command("pgaidentify", parameters=n)

    async def devdetails(self) -> dict:
        """
        API 'devdetails' command.

        Returns a dict containing all devices with their static details.
        """
        return await self.send_command("devdetails")

    async def restart(self) -> dict:
        """
        API 'restart' command.

        Returns a single "RESTART" before BMMiner restarts.
        """
        return await self.send_command("restart")

    async def stats(self) -> dict:
        """
        API 'stats' command.

        Returns a dict containing stats for all device/pool with more than 1 getwork.
        """
        return await self.send_command("stats")

    async def estats(self, old: bool = False) -> dict:
        """
        API 'estats' command.

        Returns a dict containing stats for all device/pool with more than 1 getwork,
        ignoring zombie devices.

        Parameters:
            old (optional): include zombie devices that became zombies less than 'old' seconds ago.
        """
        if old:
            return await self.send_command("estats", parameters="old")
        else:
            return await self.send_command("estats")

    async def check(self, command: str) -> dict:
        """
        API 'check' command.

        Returns information about a command:
            Exists (Y/N) <- the command exists in this version
            Access (Y/N) <- you have access to use the command

        Parameters:
            command: the command to get information about.
        """
        return await self.send_command("check", parameters=command)

    async def failover_only(self, failover: bool) -> dict:
        """
        API 'failover-only' command.

        Returns the STATUS section with what failover-only was set to.

        Parameters:
            failover: what to set failover-only to.
        """
        return await self.send_command("failover-only", parameters=failover)

    async def coin(self) -> dict:
        """
        API 'coin' command.

        Returns information about the current coin being mined:
            Hash Method <- the hashing algorithm
            Current Block Time <- blocktime as a float, 0 means none
            Current Block Hash <- the hash of the current block, blank means none
            LP <- whether LP is in use on at least 1 pool
            Network Difficulty: the current network difficulty
        """
        return await self.send_command("coin")

    async def debug(self, setting: str) -> dict:
        """
        API 'debug' command.

        Returns which debug setting was enabled or disabled.

        Parameters:
            setting: which setting to switch to. Options are:
                Silent,
                Quiet,
                Verbose,
                Debug,
                RPCProto,
                PerDevice,
                WorkTime,
                Normal.
        """
        return await self.send_command("debug", parameters=setting)

    async def setconfig(self, name: str, n: int) -> dict:
        """
        API 'setconfig' command.

        Returns the STATUS section with the results of setting 'name' to N.

        Parameters:
            name: name of the config setting to set. Options are:
                queue,
                scantime,
                expiry.
            n: the value to set the 'name' setting to.
        """
        return await self.send_command("setconfig", parameters=f"{name}, {n}")

    async def usbstats(self) -> dict:
        """
        API 'usbstats' command.

        Returns a dict containing the stats of all USB devices except ztex.
        """
        return await self.send_command("usbstats")

    async def pgaset(self, n: int, opt: str, val: int = None) -> dict:
        """
        API 'pgaset' command.

        Returns the STATUS section with the results of setting PGA N with opt[,val].

        Parameters:
            n: the PGA to set the options on.
            opt: the option to set. Setting this to 'help' returns a help message.
            val: the value to set the option to.

        Options:
            MMQ -
                opt: clock
                val: 160 - 230 (multiple of 2)
            CMR -
                opt: clock
                val: 100 - 220
        """
        if val:
            return await self.send_command("pgaset", parameters=f"{n}, {opt}, {val}")
        else:
            return await self.send_command("pgaset", parameters=f"{n}, {opt}")

    async def zero(self, which: str, summary: bool) -> dict:
        """
        API 'zero' command.

        Returns the STATUS section with info on the zero and optional summary.

        Parameters:
            which: which device to zero.
                Setting this to 'all' zeros all devices.
                Setting this to 'bestshare' zeros only the bestshare  values for each pool and global.
            summary: whether or not to show a full summary.
        """
        return await self.send_command("zero", parameters=f"{which}, {summary}")

    async def hotplug(self, n: int) -> dict:
        """
        API 'hotplug' command.

        Returns the STATUS section with whether or not hotplug was enabled.
        """
        return await self.send_command("hotplug", parameters=n)

    async def asc(self, n: int) -> dict:
        """
        API 'asc' command.

        Returns a dict containing the details of a single ASC of number N.

        n: the ASC device to get details of.
        """
        return await self.send_command("asc", parameters=n)

    async def ascenable(self, n: int) -> dict:
        """
        API 'ascenable' command.

        Returns the STATUS section with the results of enabling the ASC device N.

        Parameters:
            n: the number of the ASC to enable.
        """
        return await self.send_command("ascenable", parameters=n)

    async def ascdisable(self, n: int) -> dict:
        """
        API 'ascdisable' command.

        Returns the STATUS section with the results of disabling the ASC device N.

        Parameters:
            n: the number of the ASC to disable.

        """
        return await self.send_command("ascdisable", parameters=n)

    async def ascidentify(self, n: int) -> dict:
        """
        API 'ascidentify' command.

        Returns the STATUS section with the results of identifying the ASC device N.

        Parameters:
            n: the number of the PGA to identify.
        """
        return await self.send_command("ascidentify", parameters=n)

    async def asccount(self) -> dict:
        """
        API 'asccount' command.

        Returns a dict containing the number of ASC devices.
        """
        return await self.send_command("asccount")

    async def ascset(self, n: int, opt: str, val: int = None) -> dict:
        """
        API 'ascset' command.

        Returns the STATUS section with the results of setting ASC N with opt[,val].

        Parameters:
            n: the ASC to set the options on.
            opt: the option to set. Setting this to 'help' returns a help message.
            val: the value to set the option to.

        Options:
            AVA+BTB -
                opt: freq
                val: 256 - 1024 (chip frequency)
            BTB -
                opt: millivolts
                val: 1000 - 1400 (core voltage)
            MBA -
                opt: reset
                val: 0 - # of chips (reset a chip)

                opt: freq
                val: 0 - # of chips, 100 - 1400 (chip frequency)

                opt: ledcount
                val: 0 - 100 (chip count for LED)

                opt: ledlimit
                val: 0 - 200 (LED off below GH/s)

                opt: spidelay
                val: 0 - 9999 (SPI per I/O delay)

                opt: spireset
                val: i or s, 0 - 9999 (SPI regular reset)

                opt: spisleep
                val: 0 - 9999 (SPI reset sleep in ms)
            BMA -
                opt: volt
                val: 0 - 9

                opt: clock
                val: 0 - 15
        """
        if val:
            return await self.send_command("ascset", parameters=f"{n}, {opt}, {val}")
        else:
            return await self.send_command("ascset", parameters=f"{n}, {opt}")

    async def lcd(self) -> dict:
        """
        API 'lcd' command.

        Returns a dict containing an all in one status summary of the miner.
        """
        return await self.send_command("lcd")

    async def lockstats(self) -> dict:
        """
        API 'lockstats' command.

        Returns the STATUS section with the result of writing the lock stats to STDERR.
        """
        return await self.send_command("lockstats")
