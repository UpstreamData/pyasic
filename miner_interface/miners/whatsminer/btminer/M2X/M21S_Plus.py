from miner_interface.miners._backends import BTMiner  # noqa - Ignore access to _module
from miner_interface.miners._types import M21SPlus  # noqa - Ignore access to _module


class BTMinerM21SPlus(BTMiner, M21SPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
