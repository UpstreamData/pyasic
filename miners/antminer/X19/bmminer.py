from miners.bmminer import BMMiner


class BMMinerX19(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)

    def __repr__(self) -> str:
        return f"BMMinerX19: {str(self.ip)}"

    async def get_model(self):
        if self.model:
            return self.model
        version_data = await self.api.version()
        if version_data:
            self.model = version_data["VERSION"][0]["Type"].replace("Antminer ", "")
            return self.model
        return None
