from miners.cgminer import CGMiner


class CGMinerS19(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "CGMiner"
        self.model = "S19"
        self.nominal_chips = 114

    def __repr__(self) -> str:
        return f"CGMinerS19: {str(self.ip)}"
