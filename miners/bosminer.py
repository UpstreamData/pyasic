from miners import BaseMiner
from API.bosminer import BOSMinerAPI


class BOSminer(BaseMiner):
    def __init__(self, ip: str):
        api = BOSMinerAPI(ip)
        super().__init__(ip, api)

    def __repr__(self):
        return f"BOSminer: {str(self.ip)}"
