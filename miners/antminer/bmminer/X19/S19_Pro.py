from miners._backends import BMMiner
from miners._types import S19Pro


class BMMinerS19Pro(BMMiner, S19Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
