from miners._backends import BTMiner
from miners._types import M31SPlus


class BTMinerM31SPlus(BTMiner, M31SPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
