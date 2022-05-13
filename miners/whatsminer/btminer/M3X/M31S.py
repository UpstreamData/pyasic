from miners._backends import BTMiner
from miners._types import M31S


class BTMinerM31S(BTMiner, M31S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
