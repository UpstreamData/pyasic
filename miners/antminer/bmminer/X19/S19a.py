from miners._backends import BMMiner  # noqa - Ignore access to _module
from miners._types import S19a  # noqa - Ignore access to _module


class BMMinerS19a(BMMiner, S19a):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def get_hostname(self) -> str:
        return "?"
