from miners._backends import BTMiner
from miners._types import M20SPlus


class BTMinerM20SPlus(BTMiner, M20SPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
