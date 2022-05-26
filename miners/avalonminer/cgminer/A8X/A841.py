from miners._backends import CGMiner  # noqa - Ignore access to _module
from miners._types import Avalon841  # noqa - Ignore access to _module


class CGMinerAvalon841(CGMiner, Avalon841):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
