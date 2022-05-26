from miners._backends import CGMiner  # noqa - Ignore access to _module
from miners._types import Avalon1047  # noqa - Ignore access to _module


class CGMinerAvalon1047(CGMiner, Avalon1047):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
