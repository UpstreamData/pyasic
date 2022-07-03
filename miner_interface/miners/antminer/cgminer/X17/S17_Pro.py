from miner_interface.miners._backends import CGMiner  # noqa - Ignore access to _module
from miner_interface.miners._types import S17Pro  # noqa - Ignore access to _module


class CGMinerS17Pro(CGMiner, S17Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
