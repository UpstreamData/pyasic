from miners._backends import CGMiner
from miners._types import S17e


class CGMinerS17e(CGMiner, S17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
