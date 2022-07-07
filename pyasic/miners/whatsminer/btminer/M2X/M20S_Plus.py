from pyasic.miners._backends import BTMiner  # noqa - Ignore access to _module
from pyasic.miners._types import M20SPlus  # noqa - Ignore access to _module


class BTMinerM20SPlus(BTMiner, M20SPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
