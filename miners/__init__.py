from API.bmminer import BMMinerAPI
from API.bosminer import BOSMinerAPI
from API.cgminer import CGMinerAPI
from API.btminer import BTMinerAPI
from API.unknown import UnknownAPI
import ipaddress


class BaseMiner:
    def __init__(self, ip: str, api: BMMinerAPI | BOSMinerAPI | CGMinerAPI | BTMinerAPI | UnknownAPI) -> None:
        self.ip = ipaddress.ip_address(ip)
        self.api = api
        self.api_type = None
        self.model = None

    async def reboot(self):
        return None

    async def restart_backend(self):
        return None
