from API.btminer import BTMinerAPI
from miners import BaseMiner
from API import APIError


class BTMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = BTMinerAPI(ip)
        super().__init__(ip, api)

    def __repr__(self) -> str:
        return f"BTMiner: {str(self.ip)}"

    async def get_hostname(self) -> str:
        try:
            host_data = await self.api.get_miner_info()
            if host_data:
                return host_data["Msg"]["hostname"]
        except APIError:
            return "BTMiner Unknown"

    async def send_config(self, _):
        return None  # ignore for now

    async def restart_backend(self) -> None:
        return None

    async def reboot(self) -> None:
        return None

    async def get_config(self) -> None:
        return None
