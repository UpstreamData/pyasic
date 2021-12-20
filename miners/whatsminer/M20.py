from API.btminer import BTMinerAPI
from miners import BaseMiner


class BTMinerM20(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = BTMinerAPI(ip)
        super().__init__(ip, api)

    def __repr__(self) -> str:
        return f"M20 - BTMiner: {str(self.ip)}"

    async def get_hostname(self) -> str:
        return "BTMiner Unknown"

    async def send_config(self):
        return None  # ignore for now

    async def restart_backend(self) -> None:
        return None

    async def reboot(self) -> None:
        return None

    async def get_config(self) -> None:
        return None
