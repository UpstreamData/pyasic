from miners._backends import BMMiner  # noqa - Ignore access to _module
from miners._types import S19jPro  # noqa - Ignore access to _module


class BMMinerS19jPro(BMMiner, S19jPro):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def get_hostname(self) -> str:
        return "?"
