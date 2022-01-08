from miners.cgminer import CGMiner


class CGMinerAvalon(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "Avalon"
        self.api_type = "CGMiner"

    def __repr__(self) -> str:
        return f"CGMinerAvalon: {str(self.ip)}"
