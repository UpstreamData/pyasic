from miners._backends import BMMiner
from miners._types import T19


class BMMinerT19(BMMiner, T19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def get_hostname(self) -> str:
        return "?"
