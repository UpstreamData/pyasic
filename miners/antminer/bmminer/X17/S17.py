from miners._backends import BMMiner
from miners._types import S17


class BMMinerS17(BMMiner, S17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
