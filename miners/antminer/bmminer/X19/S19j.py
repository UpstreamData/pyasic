from miners._backends import BMMiner
from miners._types import S19j


class BMMinerS19j(BMMiner, S19j):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def get_hostname(self) -> str:
        return "?"
