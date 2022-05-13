from miners._backends import BMMiner
from miners._types import T9


class BMMinerT9(BMMiner, T9):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
