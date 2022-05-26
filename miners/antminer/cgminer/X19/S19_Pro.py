from miners._backends import CGMiner  # noqa - Ignore access to _module
from miners._types import S19Pro  # noqa - Ignore access to _module


class CGMinerS19Pro(CGMiner, S19Pro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def get_hostname(self) -> str:
        return "?"
