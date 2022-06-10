from .X17 import BMMinerX17
from miners._types import T17  # noqa - Ignore access to _module


class BMMinerT17(BMMinerX17, T17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
