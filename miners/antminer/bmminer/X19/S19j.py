from .X19 import BMMinerX19
from miners._types import S19j  # noqa - Ignore access to _module


class BMMinerS19j(BMMinerX19, S19j):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
