from API import BaseMinerAPI


class BOSMinerAPI(BaseMinerAPI):
    """An abstraction of the BOSMiner API.

    Each method corresponds to an API command in BOSMiner.

    BOSMiner API documentation:
        https://docs.braiins.com/os/plus-en/Development/1_api.html

    This class abstracts use of the BOSMiner API, as well as the
    methods for sending commands to it.  The self.send_command()
    function handles sending a command to the miner asynchronously, and
    as such is the base for many of the functions in this class, which
    rely on it to send the command for them.

    :param ip: The IP of the miner to reference the API on.
    :param port: The port to reference the API on.  Default is 4028.
    """

    def __init__(self, ip, port=4028):
        super().__init__(ip, port)

    async def asccount(self) -> dict:
        """Get data on the number of ASC devices and their info.

        :return: Data on all ASC devices.
        """
        return await self.send_command("asccount")

    async def asc(self, n: int) -> dict:
        """Get data for ASC device n.

        :param n: The device to get data for.

        :return: The data for ASC device n.
        """
        return await self.send_command("asc", parameters=n)

    async def devdetails(self) -> dict:
        """Get data on all devices with their static details.

        :return: Data on all devices with their static details.
        """
        return await self.send_command("devdetails")

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
            return await self.send_command("edevs", parameters="old")
        else:
            return await self.send_command("edevs")

    async def pools(self) -> dict:
        """Get pool information.

        :return: Miner pool information.
        """
        return await self.send_command("pools")

    async def summary(self) -> dict:
        """Get the status summary of the miner.

        :return: The status summary of the miner.
        """
        return await self.send_command("summary")

    async def stats(self) -> dict:
        """Get stats of each device/pool with more than 1 getwork.

        :return: Stats of each device/pool with more than 1 getwork.
        """
        return await self.send_command("stats")

    async def version(self) -> dict:
        """Get miner version info.

        :return: Miner version information.
        """
        return await self.send_command("version")

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
        """Check if the command command exists in BOSMiner.

        :param command: The command to check.

        :return: Information about a command:
            Exists (Y/N) <- the command exists in this version
            Access (Y/N) <- you have access to use the command
        """
        return await self.send_command("check", parameters=command)

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

    async def lcd(self) -> dict:
        """Get a general all-in-one status summary of the miner.

        :return: An all-in-one status summary of the miner.
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
        """Get fan data.

        :return: Data on the fans of the miner.
        """
        return await self.send_command("fans")

    async def tempctrl(self) -> dict:
        """Get temperature control data.

        :return: Data about the temp control settings of the miner.
        """
        return await self.send_command("tempctrl")

    async def temps(self) -> dict:
        """Get temperature data.

        :return: Data on the temps of the miner.
        """
        return await self.send_command("temps")

    async def tunerstatus(self) -> dict:
        """Get tuner status data

        :return: Data on the status of autotuning.
        """
        return await self.send_command("tunerstatus")

    async def pause(self) -> dict:
        """Pause mining.

        :return: Confirmation of pausing mining.
        """
        return await self.send_command("pause")

    async def resume(self) -> dict:
        """Resume mining.

        :return: Confirmation of resuming mining.
        """
        return await self.send_command("resume")
