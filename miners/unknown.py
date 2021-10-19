from API.unknown import UnknownAPI
from miners import BaseMiner


class UnknownMiner(BaseMiner):
    def __init__(self, ip: str):
        api = UnknownAPI(ip)
        super().__init__(ip, api)

    def __repr__(self):
        return f"Unknown: {str(self.ip)}"

    async def send_config(self):
        return None
