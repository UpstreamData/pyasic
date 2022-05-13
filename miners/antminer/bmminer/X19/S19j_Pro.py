from miners._backends import BMMiner
from miners._types import S19jPro


class BMMinerS19jPro(BMMiner, S19jPro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
