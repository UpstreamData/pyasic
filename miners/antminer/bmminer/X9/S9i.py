from miners._backends import BMMiner
from miners._types import S9i


class BMMinerS9i(BMMiner, S9i):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
