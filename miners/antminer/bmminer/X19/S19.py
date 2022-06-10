from .X19 import BMMinerX19
from miners._types import S19  # noqa - Ignore access to _module


class BMMinerS19(BMMinerX19, S19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
