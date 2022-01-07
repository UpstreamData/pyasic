from miners.cgminer import CGMiner


class CGMinerX19(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "CGMiner"

    def __repr__(self) -> str:
        return f"CGMinerX19: {str(self.ip)}"

    async def get_model(self):
        if self.model:
            return self.model
        version_data = await self.api.version()
        if version_data:
            self.model = version_data["VERSION"][0]["Type"].replace("Antminer ", "")
            return self.model
        return None
