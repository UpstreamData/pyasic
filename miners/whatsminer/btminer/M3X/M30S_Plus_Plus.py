from miners._backends import BTMiner
from miners._types import M30SPlusPlus


class BTMinerM30SPlusPlus(BTMiner, M30SPlusPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
