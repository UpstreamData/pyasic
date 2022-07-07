from pyasic.miners._backends import BTMiner  # noqa - Ignore access to _module
from pyasic.miners._types import (
    M30SPlus,
    M30SPlusVE40,
    M30SPlusVF20,
    M30SPlusVG60,
)  # noqa - Ignore access to _module


class BTMinerM30SPlus(BTMiner, M30SPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM30SPlusVE40(BTMiner, M30SPlusVE40):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM30SPlusVF20(BTMiner, M30SPlusVF20):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM30SPlusVG60(BTMiner, M30SPlusVG60):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
