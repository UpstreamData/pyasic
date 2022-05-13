from miners._backends import CGMiner
from miners._types import S19Pro


class CGMinerS19Pro(CGMiner, S19Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
