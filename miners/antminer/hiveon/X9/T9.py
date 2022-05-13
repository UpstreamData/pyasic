from miners._backends import Hiveon
from miners._types import T9


class HiveonT9(Hiveon, T9):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
