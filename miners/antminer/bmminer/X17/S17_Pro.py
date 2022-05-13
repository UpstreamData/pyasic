from miners._backends import BMMiner
from miners._types import S17Pro


class BMMinerS17Pro(BMMiner, S17Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
