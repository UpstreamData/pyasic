from pyasic.miners._backends import BOSMiner  # noqa - Ignore access to _module
from pyasic.miners._types import S17  # noqa - Ignore access to _module


class BOSMinerS17(BOSMiner, S17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
