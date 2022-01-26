from API.btminer import BTMinerAPI
from miners import BaseMiner
from API import APIError


class BTMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = BTMinerAPI(ip)
        self.model = None
        super().__init__(ip, api)

    def __repr__(self) -> str:
        return f"BTMiner: {str(self.ip)}"

    async def get_model(self):
        if self.model:
            return self.model
        version_data = await self.api.devdetails()
        if version_data:
            self.model = version_data["DEVDETAILS"][0]["Model"].split("V")[0]
            return self.model
        return None

    async def get_hostname(self) -> str:
        try:
            host_data = await self.api.get_miner_info()
            if host_data:
                return host_data["Msg"]["hostname"]
        except APIError:
            return "?"
