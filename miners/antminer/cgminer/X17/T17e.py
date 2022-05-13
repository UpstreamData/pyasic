from miners._backends import CGMiner
from miners._types import T17e


class CGMinerT17e(CGMiner, T17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
