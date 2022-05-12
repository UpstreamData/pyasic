from miners.cgminer import CGMiner


class CGMinerS17(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "CGMiner"
        self.model = "S17"
        self.nominal_chips = 65

    def __repr__(self) -> str:
        return f"CGMinerS17: {str(self.ip)}"
