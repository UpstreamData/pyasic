from miner_interface.miners._backends import BTMiner  # noqa - Ignore access to _module
from miner_interface.miners._types import M31SPlus, M31SPlusVE20  # noqa - Ignore access to _module


class BTMinerM31SPlus(BTMiner, M31SPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM31SPlusVE20(BTMiner, M31SPlusVE20):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
