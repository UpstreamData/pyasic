from miners._backends import BTMiner  # noqa - Ignore access to _module
from miners._types import M30S  # noqa - Ignore access to _module


class BTMinerM30S(BTMiner, M30S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
