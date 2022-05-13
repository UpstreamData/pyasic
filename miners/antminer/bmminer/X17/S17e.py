from miners._backends import BMMiner
from miners._types import S17e


class BMMinerS17e(BMMiner, S17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
