from miners._backends import BMMiner  # noqa - Ignore access to _module
from miners._types import T17e  # noqa - Ignore access to _module


class BMMinerT17e(BMMiner, T17e):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
