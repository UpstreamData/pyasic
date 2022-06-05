from miners._backends import Hiveon  # noqa - Ignore access to _module
from miners._types import T9  # noqa - Ignore access to _module


class HiveonT9(Hiveon, T9):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
