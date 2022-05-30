from miners._backends import BTMiner  # noqa - Ignore access to _module
from miners._types import (  # noqa - Ignore access to _module
    M30SPlusPlusVG40,
    M30SPlusPlusVG30,
)


class BTMinerM30SPlusPlusVG40(BTMiner, M30SPlusPlusVG40):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM30SPlusPlusVG30(BTMiner, M30SPlusPlusVG30):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
