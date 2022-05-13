from miners._backends import CGMiner
from miners._types import T17Plus


class CGMinerT17Plus(CGMiner, T17Plus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
