from pyasic.miners._backends import CGMiner  # noqa - Ignore access to _module
from pyasic.miners._types import T19  # noqa - Ignore access to _module


class CGMinerT19(CGMiner, T19):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def get_hostname(self) -> str:
        return "?"
