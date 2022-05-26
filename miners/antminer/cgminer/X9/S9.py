from miners._backends import CGMiner  # noqa - Ignore access to _module
from miners._types import S9  # noqa - Ignore access to _module


class CGMinerS9(CGMiner, S9):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
