from API.bmminer import BMMinerAPI
from miners import BaseMiner


class BMMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = BMMinerAPI(ip)
        self.model = None
        super().__init__(ip, api)

    def __repr__(self) -> str:
        return f"BMMiner: {str(self.ip)}"

    async def get_model(self):
        if self.model:
            return self.model
        version_data = await self.api.devdetails()
        if version_data:
            self.model = version_data["DEVDETAILS"][0]["Model"].replace("Antminer ", "")
            return self.model
        return None


    async def get_hostname(self) -> str:
        return "BMMiner Unknown"

    async def send_config(self, _):
        return None  # ignore for now

    async def restart_backend(self) -> None:
        return None  # Murray

    async def reboot(self) -> None:
        return None  # Murray

    async def get_config(self) -> None:
        return None  # Murray
