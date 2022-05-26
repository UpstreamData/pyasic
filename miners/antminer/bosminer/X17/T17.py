from miners._backends import BOSMiner  # noqa - Ignore access to _module
from miners._types import T17  # noqa - Ignore access to _module


class BOSMinerT17(BOSMiner, T17):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
