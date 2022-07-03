from miner_interface.miners._backends import BTMiner  # noqa - Ignore access to _module
from miner_interface.miners._types import M32S  # noqa - Ignore access to _module


class BTMinerM32S(BTMiner, M32S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
