from pyasic.miners._backends.cgminer import CGMiner  # noqa - Ignore access to _module
from pyasic.miners._types.antminer import T9  # noqa - Ignore access to _module


class CGMinerT9(CGMiner, T9):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "T9"
        self.api_type = "CGMiner"
