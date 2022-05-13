from miners._backends import BTMiner
from miners._types import M32S


class BTMinerM32S(BTMiner, M32S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
