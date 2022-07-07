from pyasic.miners._backends import CGMiner  # noqa - Ignore access to _module
from pyasic.miners._types import S17Plus  # noqa - Ignore access to _module


class CGMinerS17Plus(CGMiner, S17Plus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
