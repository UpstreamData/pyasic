from miners._backends import BOSMiner
from miners._types import T17e


class BOSMinerT17e(BOSMiner, T17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
