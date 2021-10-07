from miners import BaseMiner
from API.bosminer import BOSMinerAPI
from API.bmminer import BMMinerAPI
from API.cgminer import CGMinerAPI


class BMMiner(BaseMiner):
    def __init__(self, ip: str):
        api = BMMinerAPI(ip)
        super().__init__(ip, api)

    def __repr__(self):
        return f"BMMiner: {str(self.ip)}"
