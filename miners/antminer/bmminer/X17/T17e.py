from .X17 import BMMinerX17
from miners._types import T17e  # noqa - Ignore access to _module


class BMMinerT17e(BMMinerX17, T17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
