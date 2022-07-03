from .X17 import BMMinerX17
from miner_interface.miners._types import S17e  # noqa - Ignore access to _module


class BMMinerS17e(BMMinerX17, S17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
