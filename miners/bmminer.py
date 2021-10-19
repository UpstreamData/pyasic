from API.bmminer import BMMinerAPI
from miners import BaseMiner


class BMMiner(BaseMiner):
    def __init__(self, ip: str):
        api = BMMinerAPI(ip)
        super().__init__(ip, api)

    def __repr__(self):
        return f"BMMiner: {str(self.ip)}"

    async def send_config(self):
        return None
