from pyasic.miners._backends import BTMiner  # noqa - Ignore access to _module
from pyasic.miners._types import (
    M30S,
    M30SV50,
    M30SVG20,
    M30SVE20,
    M30SVE10,
)  # noqa - Ignore access to _module


class BTMinerM30S(BTMiner, M30S):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM30SVE10(BTMiner, M30SVE10):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM30SVG20(BTMiner, M30SVG20):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM30SVE20(BTMiner, M30SVE20):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip


class BTMinerM30SV50(BTMiner, M30SV50):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
