from miner_interface.API.unknown import UnknownAPI
from miner_interface.miners import BaseMiner


class UnknownMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        super().__init__()
        self.ip = ip
        self.api = UnknownAPI(ip)
        self.model = "Unknown"

    def __repr__(self) -> str:
        return f"Unknown: {str(self.ip)}"

    async def get_model(self):
        return "Unknown"

    async def get_hostname(self):
        return "Unknown"
