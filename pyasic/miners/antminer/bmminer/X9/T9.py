from pyasic.miners._backends import BMMiner  # noqa - Ignore access to _module
from pyasic.miners._types import T9  # noqa - Ignore access to _module


class BMMinerT9(BMMiner, T9):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
