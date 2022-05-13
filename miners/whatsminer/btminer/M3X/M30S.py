from miners._backends import BTMiner
from miners._types import M30S


class BTMinerM30S(BTMiner, M30S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
