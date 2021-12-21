from API.unknown import UnknownAPI
from miners import BaseMiner


class UnknownMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = UnknownAPI(ip)
        super().__init__(ip, api)

    def __repr__(self) -> str:
        return f"Unknown: {str(self.ip)}"

    async def send_config(self, _):
        return None

    async def get_hostname(self):
        return "Unknown"
