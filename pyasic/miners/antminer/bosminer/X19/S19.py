from pyasic.miners._backends import BOSMiner  # noqa - Ignore access to _module
from pyasic.miners._types import S19  # noqa - Ignore access to _module


class BOSMinerS19(BOSMiner, S19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
