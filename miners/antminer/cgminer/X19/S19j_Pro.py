from miners._backends import CGMiner
from miners._types import S19jPro


class CGMinerS19jPro(CGMiner, S19jPro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
