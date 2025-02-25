from pyasic.rpc.base import BaseMinerRPCAPI


class MaraRPCAPI(BaseMinerRPCAPI):
    """An abstraction of the MaraFW API.

    Each method corresponds to an API command in MaraFW.

    No documentation for this API is currently publicly available.

    Additionally, every command not included here just returns the result of the `summary` command.

    This class abstracts use of the MaraFW API, as well as the
    methods for sending commands to it.  The `self.send_command()`
    function handles sending a command to the miner asynchronously, and
    as such is the base for many of the functions in this class, which
    rely on it to send the command for them.
    """

    async def summary(self):
        return await self.send_command("summary")

    async def devs(self):
        return await self.send_command("devs")

    async def pools(self):
        return await self.send_command("pools")

    async def stats(self):
        return await self.send_command("stats")

    async def version(self):
        return await self.send_command("version")
