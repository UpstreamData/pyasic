from .X19 import BMMinerX19
from miner_interface.miners._types import S19Pro  # noqa - Ignore access to _module


class BMMinerS19Pro(BMMinerX19, S19Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
