from miners._backends import CGMiner
from miners._types import S9


class CGMinerS9(CGMiner, S9):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
