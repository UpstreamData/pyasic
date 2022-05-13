from miners._backends import CGMiner
from miners._types import Avalon1066


class CGMinerAvalon1066(CGMiner, Avalon1066):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
