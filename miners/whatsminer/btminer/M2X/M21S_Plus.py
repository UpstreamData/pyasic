from miners._backends import BTMiner
from miners._types import M21SPlus


class BTMinerM21SPlus(BTMiner, M21SPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
