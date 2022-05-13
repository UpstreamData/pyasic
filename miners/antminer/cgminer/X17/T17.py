from miners._backends import CGMiner
from miners._types import T17


class CGMinerT17(CGMiner, T17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
