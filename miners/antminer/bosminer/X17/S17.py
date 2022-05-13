from miners._backends import BOSMiner
from miners._types import S17


class BOSMinerS17(BOSMiner, S17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
