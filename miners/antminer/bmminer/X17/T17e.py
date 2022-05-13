from miners._backends import BMMiner
from miners._types import T17e


class BMMinerT17e(BMMiner, T17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
