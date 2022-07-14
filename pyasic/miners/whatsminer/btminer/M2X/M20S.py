from pyasic.miners._backends import BTMiner  # noqa - Ignore access to _module
from pyasic.miners._types import (  # noqa - Ignore access to _module
    M20S,
    M20SV10,
    M20SV20,
)


class BTMinerM20S(BTMiner, M20S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM20SV10(BTMiner, M20SV10):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM20SV20(BTMiner, M20SV20):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
