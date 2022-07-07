from .X19 import BMMinerX19
from pyasic.miners._types import S19jPro  # noqa - Ignore access to _module


class BMMinerS19jPro(BMMinerX19, S19jPro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
