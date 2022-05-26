from miners._backends import BTMiner  # noqa - Ignore access to _module
from miners._types import M31S  # noqa - Ignore access to _module


class BTMinerM31S(BTMiner, M31S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
