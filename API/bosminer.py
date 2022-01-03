from API import BaseMinerAPI


class BOSMinerAPI(BaseMinerAPI):
    """
    A class that abstracts the BOSMiner API in the miners.

    Each method corresponds to an API command in BOSMiner.

    BOSMiner API documentation:
        https://docs.braiins.com/os/plus-en/Development/1_api.html

    Parameters:
        ip: the IP address of the miner.
        port (optional): the port of the API on the miner (standard is 4028)
    """
    def __init__(self, ip, port=4028):
        super().__init__(ip, port)

    async def asccount(self) -> dict:
        """
        API 'asccount' command.

        Returns a dict containing the number of ASC devices.
        """
        return await self.send_command("asccount")

    async def asc(self, n: int) -> dict:
        """
        API 'asc' command.

        Returns a dict containing the details of a single ASC of number N.

        n: the ASC device to get details of.
        """
        return await self.send_command("asc", parameters=n)

    async def devdetails(self) -> dict:
        """
        API 'devdetails' command.

        Returns a dict containing all devices with their static details.
        """
        return await self.send_command("devdetails")

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

    async def pools(self) -> dict:
        """
        API 'pools' command.

        Returns a dict containing the status of each pool.
        """
        return await self.send_command("pools")

    async def summary(self) -> dict:
        """
        API 'summary' command.

        Returns a dict containing the status summary of the miner.
        """
        return await self.send_command("summary")

    async def stats(self) -> dict:
        """
        API 'stats' command.

        Returns a dict containing stats for all device/pool with more than 1 getwork.
        """
        return await self.send_command("stats")

    async def version(self) -> dict:
        """
        API 'version' command.

        Returns a dict containing version information.
        """
        return await self.send_command("version")

    async def estats(self) -> dict:
        """
        API 'estats' command.

        Returns a dict containing stats for all device/pool with more than 1 getwork,
        ignoring zombie devices.

        Parameters:
            old (optional): include zombie devices that became zombies less than 'old' seconds ago.
        """
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

    async def lcd(self) -> dict:
        """
        API 'lcd' command.

        Returns a dict containing an all in one status summary of the miner.
        """
        return await self.send_command("lcd")

    async def switchpool(self, n: int) -> dict:
        # BOS has not implemented this yet, they will in the future
        raise NotImplementedError
        # return await self.send_command("switchpool", parameters=n)

    async def enablepool(self, n: int) -> dict:
        # BOS has not implemented this yet, they will in the future
        raise NotImplementedError
        # return await self.send_command("enablepool", parameters=n)

    async def disablepool(self, n: int) -> dict:
        # BOS has not implemented this yet, they will in the future
        raise NotImplementedError
        # return await self.send_command("disablepool", parameters=n)

    async def addpool(self, url: str, username: str, password: str) -> dict:
        # BOS has not implemented this yet, they will in the future
        raise NotImplementedError
        # return await self.send_command("addpool", parameters=f"{url}, {username}, {password}")

    async def removepool(self, n: int) -> dict:
        # BOS has not implemented this yet, they will in the future
        raise NotImplementedError
        # return await self.send_command("removepool", parameters=n)

    async def fans(self) -> dict:
        """
        API 'fans' command.

        Returns a dict containing information on fans and fan speeds.
        """
        return await self.send_command("fans")

    async def tempctrl(self) -> dict:
        """
        API 'tempctrl' command.

        Returns a dict containing temp control configuration.
        """
        return await self.send_command("tempctrl")

    async def temps(self) -> dict:
        """
        API 'temps' command.

        Returns a dict containing temperature information.
        """
        return await self.send_command("temps")

    async def tunerstatus(self) -> dict:
        """
        API 'tunerstatus' command.

        Returns a dict containing tuning stats.
        """
        return await self.send_command("tunerstatus")

    async def pause(self) -> dict:
        """
        API 'pause' command.

        Pauses mining and stops power consumption and waits for resume command.
        """
        return await self.send_command("pause")

    async def resume(self) -> dict:
        """
        API 'pause' command.

        Resumes mining on the miner.
        """
        return await self.send_command("resume")
