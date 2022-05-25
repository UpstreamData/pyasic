from miners._backends import CGMiner
from miners._types import T19


class CGMinerT19(CGMiner, T19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def get_hostname(self) -> str:
        return "?"
