from pyasic.miners._backends import BOSMiner  # noqa - Ignore access to _module
from pyasic.miners._types import T19  # noqa - Ignore access to _module


class BOSMinerT19(BOSMiner, T19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
