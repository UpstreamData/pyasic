from miners._backends import BMMiner
from miners._types import S9


class BMMinerS9(BMMiner, S9):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
