from API.bmminer import BMMinerAPI
from API.bosminer import BOSMinerAPI
from API.cgminer import CGMinerAPI
import ipaddress


class BaseMiner:
    def __init__(self, ip: str, api: BMMinerAPI or BOSMinerAPI or CGMinerAPI) -> None:
        self.ip = ipaddress.ip_address(ip)
        self.api = api
