from miners._backends import BTMiner
from miners._types import M20S


class BTMinerM20S(BTMiner, M20S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
