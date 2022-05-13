from miners._backends import CGMiner
from miners._types import S17Pro


class CGMinerS17Pro(CGMiner, S17Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
