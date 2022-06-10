from .X17 import BMMinerX17
from miners._types import S17Plus  # noqa - Ignore access to _module


class BMMinerS17Plus(BMMinerX17, S17Plus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
