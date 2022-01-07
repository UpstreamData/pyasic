from miners.cgminer import CGMiner


class CGMinerS9(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "S9"
        self.api_type = "CGMiner"

    def __repr__(self) -> str:
        return f"CGMinerS9: {str(self.ip)}"
