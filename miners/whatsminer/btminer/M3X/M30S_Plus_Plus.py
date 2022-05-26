from miners._backends import BTMiner  # noqa - Ignore access to _module
from miners._types import M30SPlusPlus  # noqa - Ignore access to _module


class BTMinerM30SPlusPlus(BTMiner, M30SPlusPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
