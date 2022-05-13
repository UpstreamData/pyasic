from miners._backends import BTMiner
from miners._types import M21


class BTMinerM21(BTMiner, M21):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
