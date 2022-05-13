from miners._backends import BOSMiner
from miners._types import T17Plus


class BOSMinerT17Plus(BOSMiner, T17Plus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
