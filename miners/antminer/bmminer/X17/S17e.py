from miners._backends import BMMiner  # noqa - Ignore access to _module
from miners._types import S17e  # noqa - Ignore access to _module


class BMMinerS17e(BMMiner, S17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
