from miners._backends import CGMiner  # noqa - Ignore access to _module
from miners._types import Avalon1066  # noqa - Ignore access to _module


class CGMinerAvalon1066(CGMiner, Avalon1066):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
