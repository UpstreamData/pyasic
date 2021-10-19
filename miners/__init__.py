from API import BaseMinerAPI
import ipaddress
import typing


class BaseMiner:
    def __init__(self, ip: str, api: typing.Type[BaseMinerAPI]):
        self.ip = ipaddress.ip_address(ip)
        self.api = api
