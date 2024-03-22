from pyasic.rpc.bmminer import BMMinerRPCAPI


class AntminerRPCAPI(BMMinerRPCAPI):
    async def stats(self, new_api: bool = False) -> dict:
        if new_api:
            return await self.send_command("stats", new_api=True)
        return await super().stats()

    async def rate(self):
        return await self.send_command("rate", new_api=True)

    async def pools(self, new_api: bool = False):
        if new_api:
            return await self.send_command("pools", new_api=True)
        return await self.send_command("pools")

    async def reload(self):
        return await self.send_command("reload", new_api=True)

    async def summary(self, new_api: bool = False):
        if new_api:
            return await self.send_command("summary", new_api=True)
        return await self.send_command("summary")

    async def warning(self):
        return await self.send_command("warning", new_api=True)

    async def new_api_pools(self):
        return await self.pools(new_api=True)

    async def new_api_stats(self):
        return await self.stats(new_api=True)

    async def new_api_summary(self):
        return await self.summary(new_api=True)
