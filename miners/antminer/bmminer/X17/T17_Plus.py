from miners._backends import BMMiner
from miners._types import T17Plus


class BMMinerT17Plus(BMMiner, T17Plus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
