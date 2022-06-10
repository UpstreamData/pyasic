from .X17 import BMMinerX17
from miners._types import T17Plus  # noqa - Ignore access to _module


class BMMinerT17Plus(BMMinerX17, T17Plus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
