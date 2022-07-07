from pyasic.miners._backends import BTMiner  # noqa - Ignore access to _module
from pyasic.miners._types import M20S  # noqa - Ignore access to _module


class BTMinerM20S(BTMiner, M20S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
