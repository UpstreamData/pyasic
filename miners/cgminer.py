from miners import BaseMiner
from API.bosminer import BOSMinerAPI
from API.bmminer import BMMinerAPI
from API.cgminer import CGMinerAPI


class CGMiner(BaseMiner):
    def __init__(self, ip: str):
        api = CGMinerAPI(ip)
        super().__init__(ip, api)

    def __repr__(self):
        return f"CGMiner: {str(self.ip)}"
