from miners._backends import BOSMiner
from miners._types import S19jPro


class BOSMinerS19jPro(BOSMiner, S19jPro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
