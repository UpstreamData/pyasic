from pyasic.miners._backends import CGMiner  # noqa - Ignore access to _module
from pyasic.miners._types import T17e  # noqa - Ignore access to _module


class CGMinerT17e(CGMiner, T17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
