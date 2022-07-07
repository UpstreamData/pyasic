from pyasic.miners._backends import BMMiner  # noqa - Ignore access to _module
from pyasic.miners._types import S9i  # noqa - Ignore access to _module


class BMMinerS9i(BMMiner, S9i):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
