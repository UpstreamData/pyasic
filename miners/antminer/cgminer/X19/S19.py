from miners._backends import CGMiner
from miners._types import S19


class CGMinerS19(CGMiner, S19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def get_hostname(self) -> str:
        return "?"
