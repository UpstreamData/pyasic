from miners._backends import BOSMiner
from miners._types import S9


class BOSMinerS9(BOSMiner, S9):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
