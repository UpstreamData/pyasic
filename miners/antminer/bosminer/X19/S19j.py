from miners._backends import BOSMiner
from miners._types import S19j


class BOSMinerS19j(BOSMiner, S19j):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
