from miner_interface.miners._backends import BOSMiner  # noqa - Ignore access to _module
from miner_interface.miners._types import S19j  # noqa - Ignore access to _module


class BOSMinerS19j(BOSMiner, S19j):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
