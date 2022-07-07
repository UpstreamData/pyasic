from pyasic.miners._backends import BOSMiner  # noqa - Ignore access to _module
from pyasic.miners._types import T17e  # noqa - Ignore access to _module


class BOSMinerT17e(BOSMiner, T17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
