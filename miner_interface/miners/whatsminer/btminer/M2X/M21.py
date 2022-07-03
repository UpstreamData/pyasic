from miner_interface.miners._backends import BTMiner  # noqa - Ignore access to _module
from miner_interface.miners._types import M21  # noqa - Ignore access to _module


class BTMinerM21(BTMiner, M21):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
