from miners._backends import BOSMiner
from miners._types import S17Pro


class BOSMinerS17Pro(BOSMiner, S17Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
