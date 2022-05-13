from miners._backends import BOSMiner
from miners._types import T17


class BOSMinerT17(BOSMiner, T17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
