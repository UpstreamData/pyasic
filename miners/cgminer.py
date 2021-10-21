from API.cgminer import CGMinerAPI
from miners import BaseMiner


class CGMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = CGMinerAPI(ip)
        super().__init__(ip, api)

    def __repr__(self) -> str:
        return f"CGMiner: {str(self.ip)}"

    async def send_config(self):
        return None # ignore for now

    async def restart_backend(self) -> None:
        return None # Murray

    async def reboot(self) -> None:
        return None # Murray


    async def get_config(self) -> None:
        return None # Murray
