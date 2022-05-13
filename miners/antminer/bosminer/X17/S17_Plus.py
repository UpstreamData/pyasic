from miners._backends import BOSMiner
from miners._types import S17Plus


class BOSMinerS17Plus(BOSMiner, S17Plus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
