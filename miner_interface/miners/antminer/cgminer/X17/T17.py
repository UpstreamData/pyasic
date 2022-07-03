from miner_interface.miners._backends import CGMiner  # noqa - Ignore access to _module
from miner_interface.miners._types import T17  # noqa - Ignore access to _module


class CGMinerT17(CGMiner, T17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
