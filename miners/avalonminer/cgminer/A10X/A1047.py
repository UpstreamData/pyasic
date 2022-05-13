from miners._backends import CGMiner
from miners._types import Avalon1047


class CGMinerAvalon1047(CGMiner, Avalon1047):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
