from miners._backends import BMMiner
from miners._types import T17


class BMMinerT17(BMMiner, T17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
