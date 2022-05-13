from miners._backends import BMMiner
from miners._types import S17Plus


class BMMinerS17Plus(BMMiner, S17Plus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
