from miners._backends import CGMiner  # noqa - Ignore access to _module
from miners._types import S17  # noqa - Ignore access to _module


class CGMinerS17(CGMiner, S17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
