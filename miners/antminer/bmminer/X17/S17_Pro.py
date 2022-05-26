from miners._backends import BMMiner  # noqa - Ignore access to _module
from miners._types import S17Pro  # noqa - Ignore access to _module


class BMMinerS17Pro(BMMiner, S17Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
