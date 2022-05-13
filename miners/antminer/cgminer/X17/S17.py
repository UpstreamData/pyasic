from miners._backends import CGMiner
from miners._types import S17


class CGMinerS17(CGMiner, S17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
