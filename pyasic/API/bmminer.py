from pyasic.API import BaseMinerAPI


class BMMinerAPI(BaseMinerAPI):
    """An abstraction of the BMMiner API.

    Each method corresponds to an API command in BMMiner.

    BMMiner API documentation:
        https://github.com/jameshilliard/bmminer/blob/master/API-README

    This class abstracts use of the BMMiner API, as well as the
    methods for sending commands to it.  The self.send_command()
    function handles sending a command to the miner asynchronously, and
    as such is the base for many of the functions in this class, which
    rely on it to send the command for them.

    :param ip: The IP of the miner to reference the API on.
    :param port: The port to reference the API on.  Default is 4028.
    """

    def __init__(self, ip: str, port: int = 4028) -> None:
        super().__init__(ip, port)

    async def version(self) -> dict:
        """Get miner version info.

        :return: Miner version information.
        """
        return await self.send_command("version")

    async def config(self) -> dict:
        """Get some basic configuration info.

        :return: Some miner configuration information:
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
        """Get the status summary of the miner.

        :return: The status summary of the miner.
        """
        return await self.send_command("summary")

    async def pools(self) -> dict:
        """Get pool information.

        :return: Miner pool information.
        """
        return await self.send_command("pools")

    async def devs(self) -> dict:
        """Get data on each PGA/ASC with their details.

        :return: Data on each PGA/ASC with their details.
        """
        return await self.send_command("devs")

    async def edevs(self, old: bool = False) -> dict:
        """Get data on each PGA/ASC with their details, ignoring
         blacklisted and zombie devices.

        :param old: Include zombie devices that became zombies less
        than 'old' seconds ago

        :return: Data on each PGA/ASC with their details.
        """
        if old:
            return await self.send_command("edevs", parameters=old)
        else:
            return await self.send_command("edevs")

    async def pga(self, n: int) -> dict:
        """Get data from PGA n.

        :param n: The PGA number to get data from.

        :return: Data on the PGA n.
        """
        return await self.send_command("pga", parameters=n)

    async def pgacount(self) -> dict:
        """Get data fon all PGAs.

        :return: Data on the PGAs connected.
        """
        return await self.send_command("pgacount")

    async def switchpool(self, n: int) -> dict:
        """Switch pools to pool n.

        :param n: The pool to switch to.

        :return: A confirmation of switching to pool n.
        """
        return await self.send_command("switchpool", parameters=n)

    async def enablepool(self, n: int) -> dict:
        """Enable pool n.

        :param n: The pool to enable.

        :return: A confirmation of enabling pool n.
        """
        return await self.send_command("enablepool", parameters=n)

    async def addpool(self, url: str, username: str, password: str) -> dict:
        """Add a pool to the miner.

        :param url: The URL of the new pool to add.
        :param username: The users username on the new pool.
        :param password: The worker password on the new pool.

        :return: A confirmation of adding the pool.
        """
        return await self.send_command(
            "addpool", parameters=f"{url},{username},{password}"
        )

    async def poolpriority(self, *n: int) -> dict:
        """Set pool priority.

        :param n: Pools in order of priority.

        :return: A confirmation of setting pool priority.
        """
        pools = f"{','.join([str(item) for item in n])}"
        return await self.send_command("poolpriority", parameters=pools)

    async def poolquota(self, n: int, q: int) -> dict:
        """Set pool quota.

        :param n: Pool number to set quota on.
        :param q: Quota to set the pool to.

        :return: A confirmation of setting pool quota.
        """
        return await self.send_command("poolquota", parameters=f"{n},{q}")

    async def disablepool(self, n: int) -> dict:
        """Disable a pool.

        :param n: Pool to disable.

        :return: A confirmation of diabling the pool.
        """
        return await self.send_command("disablepool", parameters=n)

    async def removepool(self, n: int) -> dict:
        """Remove a pool.

        :param n: Pool to remove.

        :return: A confirmation of removing the pool.
        """
        return await self.send_command("removepool", parameters=n)

    async def save(self, filename: str = None) -> dict:
        """Save the config.

        :param filename: Filename to save the config as.

        :return: A confirmation of saving the config.
        """
        if filename:
            return await self.send_command("save", parameters=filename)
        else:
            return await self.send_command("save")

    async def quit(self) -> dict:
        """Quit BMMiner.

        :return: A single "BYE" before BMMiner quits.
        """
        return await self.send_command("quit")

    async def notify(self) -> dict:
        """Notify the user of past errors.

        :return: The last status and count of each devices problem(s).
        """
        return await self.send_command("notify")

    async def privileged(self) -> dict:
        """Check if you have privileged access.

        :return: The STATUS section with an error if you have no
        privileged access, or success if you have privileged access.
        """
        return await self.send_command("privileged")

    async def pgaenable(self, n: int) -> dict:
        """Enable PGA n.

        :param n: The PGA to enable.

        :return: A confirmation of enabling PGA n.
        """
        return await self.send_command("pgaenable", parameters=n)

    async def pgadisable(self, n: int) -> dict:
        """Disable PGA n.

        :param n: The PGA to disable.

        :return: A confirmation of disabling PGA n.
        """
        return await self.send_command("pgadisable", parameters=n)

    async def pgaidentify(self, n: int) -> dict:
        """Identify PGA n.

        :param n: The PGA to identify.

        :return: A confirmation of identifying PGA n.
        """
        return await self.send_command("pgaidentify", parameters=n)

    async def devdetails(self) -> dict:
        """Get data on all devices with their static details.

        :return: Data on all devices with their static details.
        """
        return await self.send_command("devdetails")

    async def restart(self) -> dict:
        """Restart BMMiner using the API.

        :return: A reply informing of the restart.
        """
        return await self.send_command("restart")

    async def stats(self) -> dict:
        """Get stats of each device/pool with more than 1 getwork.

        :return: Stats of each device/pool with more than 1 getwork.
        """
        return await self.send_command("stats")

    async def estats(self, old: bool = False) -> dict:
        """Get stats of each device/pool with more than 1 getwork,
        ignoring zombie devices.

        :param old: Include zombie devices that became zombies less
        than 'old' seconds ago.

        :return: Stats of each device/pool with more than 1 getwork,
        ignoring zombie devices.
        """
        if old:
            return await self.send_command("estats", parameters=old)
        else:
            return await self.send_command("estats")

    async def check(self, command: str) -> dict:
        """Check if the command command exists in BMMiner.

        :param command: The command to check.

        :return: Information about a command:
            Exists (Y/N) <- the command exists in this version
            Access (Y/N) <- you have access to use the command
        """
        return await self.send_command("check", parameters=command)

    async def failover_only(self, failover: bool) -> dict:
        """Set failover-only.


        :param failover: What to set failover-only to.

        :return: Confirmation of setting failover-only.
        """
        return await self.send_command("failover-only", parameters=failover)

    async def coin(self) -> dict:
        """Get information on the current coin.

        :return: Information about the current coin being mined:
            Hash Method <- the hashing algorithm
            Current Block Time <- blocktime as a float, 0 means none
            Current Block Hash <- the hash of the current block, blank
            means none
            LP <- whether LP is in use on at least 1 pool
            Network Difficulty: the current network difficulty
        """
        return await self.send_command("coin")

    async def debug(self, setting: str) -> dict:
        """Set a debug setting.

        :param setting: Which setting to switch to. Options are:
                Silent,
                Quiet,
                Verbose,
                Debug,
                RPCProto,
                PerDevice,
                WorkTime,
                Normal.

        :return: Data on which debug setting was enabled or disabled.
        """
        return await self.send_command("debug", parameters=setting)

    async def setconfig(self, name: str, n: int) -> dict:
        """Set config of name to value n.

        :param name: The name of the config setting to set. Options are:
                queue,
                scantime,
                expiry.
        :param n: The value to set the 'name' setting to.

        :return: The results of setting config of name to n.
        """
        return await self.send_command("setconfig", parameters=f"{name},{n}")

    async def usbstats(self) -> dict:
        """Get stats of all USB devices except ztex.

        :return: The stats of all USB devices except ztex.
        """
        return await self.send_command("usbstats")

    async def pgaset(self, n: int, opt: str, val: int = None) -> dict:
        """Set PGA option opt to val on PGA n.

        Options:
            MMQ -
                opt: clock
                val: 160 - 230 (multiple of 2)
            CMR -
                opt: clock
                val: 100 - 220

        :param n: The PGA to set the options on.
        :param opt: The option to set. Setting this to 'help'
        returns a help message.
        :param val: The value to set the option to.

        :return: Confirmation of setting PGA n with opt[,val].
        """
        if val:
            return await self.send_command("pgaset", parameters=f"{n},{opt},{val}")
        else:
            return await self.send_command("pgaset", parameters=f"{n},{opt}")

    async def zero(self, which: str, summary: bool) -> dict:
        """Zero a device.

        :param which: Which device to zero.
            Setting this to 'all' zeros all devices.
            Setting this to 'bestshare' zeros only the bestshare  values
            for each pool and global.
        :param summary: Whether or not to show a full summary.


        :return: the STATUS section with info on the zero and optional
        summary.
        """
        return await self.send_command("zero", parameters=f"{which},{summary}")

    async def hotplug(self, n: int) -> dict:
        """Enable hotplug.

        :param n: The device number to set hotplug on.

        :return: Information on hotplug status.
        """
        return await self.send_command("hotplug", parameters=n)

    async def asc(self, n: int) -> dict:
        """Get data for ASC device n.

        :param n: The device to get data for.

        :return: The data for ASC device n.
        """
        return await self.send_command("asc", parameters=n)

    async def ascenable(self, n: int) -> dict:
        """Enable ASC device n.

        :param n: The device to enable.

        :return: Confirmation of enabling ASC device n.
        """
        return await self.send_command("ascenable", parameters=n)

    async def ascdisable(self, n: int) -> dict:
        """Disable ASC device n.

        :param n: The device to disable.

        :return: Confirmation of disabling ASC device n.
        """
        return await self.send_command("ascdisable", parameters=n)

    async def ascidentify(self, n: int) -> dict:
        """Identify ASC device n.

        :param n: The device to identify.

        :return: Confirmation of identifying ASC device n.
        """
        return await self.send_command("ascidentify", parameters=n)

    async def asccount(self) -> dict:
        """Get data on the number of ASC devices and their info.

        :return: Data on all ASC devices.
        """
        return await self.send_command("asccount")

    async def ascset(self, n: int, opt: str, val: int = None) -> dict:
        """Set ASC n option opt to value val.

        Sets an option on the ASC n to a value.  Allowed options are:
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


        :param n: The ASC to set the options on.
        :param opt: The option to set. Setting this to 'help' returns a
        help message.
        :param val: The value to set the option to.

        :return: Confirmation of setting option opt to value val.
        """
        if val:
            return await self.send_command("ascset", parameters=f"{n},{opt},{val}")
        else:
            return await self.send_command("ascset", parameters=f"{n},{opt}")

    async def lcd(self) -> dict:
        """Get a general all-in-one status summary of the miner.

        :return: An all-in-one status summary of the miner.
        """
        return await self.send_command("lcd")

    async def lockstats(self) -> dict:
        """Write lockstats to STDERR.

        :return: The result of writing the lock stats to STDERR.
        """
        return await self.send_command("lockstats")
