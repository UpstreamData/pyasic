from miners._backends import CGMiner
from miners._types import Avalon821


class CGMinerAvalon821(CGMiner, Avalon821):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
