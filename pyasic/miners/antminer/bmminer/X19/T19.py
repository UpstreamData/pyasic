from .X19 import BMMinerX19
from pyasic.miners._types import T19  # noqa - Ignore access to _module


class BMMinerT19(BMMinerX19, T19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
