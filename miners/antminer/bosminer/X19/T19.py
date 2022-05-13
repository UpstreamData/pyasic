from miners._backends import BOSMiner
from miners._types import T19


class BOSMinerT19(BOSMiner, T19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
