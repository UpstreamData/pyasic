from miners._backends import BOSMiner
from miners._types import S17e


class BOSMinerS17e(BOSMiner, S17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
