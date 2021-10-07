import ipaddress


class UnknownMiner():
    def __init__(self, ip: str):
        self.ip = ipaddress.ip_address(ip)

    def __repr__(self):
        return f"Unknown: {str(self.ip)}"
