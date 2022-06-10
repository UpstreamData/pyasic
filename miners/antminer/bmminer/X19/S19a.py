from .X19 import BMMinerX19
from miners._types import S19a  # noqa - Ignore access to _module


class BMMinerS19a(BMMinerX19, S19a):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
