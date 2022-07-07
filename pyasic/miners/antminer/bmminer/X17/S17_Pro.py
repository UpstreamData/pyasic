from .X17 import BMMinerX17
from pyasic.miners._types import S17Pro  # noqa - Ignore access to _module


class BMMinerS17Pro(BMMinerX17, S17Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
