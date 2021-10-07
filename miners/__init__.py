from API.bosminer import BOSMinerAPI
from API.cgminer import CGMinerAPI
from API.bmminer import BMMinerAPI
import ipaddress


class BaseMiner:
    def __init__(self, ip: str, api: BOSMinerAPI or CGMinerAPI or BMMinerAPI):
        self.ip = ipaddress.ip_address(ip)
        self.api = api
