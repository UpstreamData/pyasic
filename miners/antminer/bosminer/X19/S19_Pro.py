from miners._backends import BOSMiner
from miners._types import S19Pro


class BOSMinerS19Pro(BOSMiner, S19Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
