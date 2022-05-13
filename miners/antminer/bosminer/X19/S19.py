from miners._backends import BOSMiner
from miners._types import S19


class BOSMinerS19(BOSMiner, S19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
