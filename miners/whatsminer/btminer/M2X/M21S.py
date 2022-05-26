from miners._backends import BTMiner  # noqa - Ignore access to _module
from miners._types import M21S  # noqa - Ignore access to _module


class BTMinerM21S(BTMiner, M21S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
