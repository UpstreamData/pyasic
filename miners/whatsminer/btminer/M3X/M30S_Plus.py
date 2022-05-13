from miners._backends import BTMiner
from miners._types import M30SPlus


class BTMinerM30SPlus(BTMiner, M30SPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
