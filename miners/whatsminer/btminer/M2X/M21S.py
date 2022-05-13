from miners._backends import BTMiner
from miners._types import M21S


class BTMinerM21S(BTMiner, M21S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
