from miners._backends import CGMiner
from miners._types import Avalon841


class CGMinerAvalon841(CGMiner, Avalon841):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
