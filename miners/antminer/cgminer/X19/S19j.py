from miners.cgminer import CGMiner


class CGMinerS19j(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "CGMiner"
        self.model = "S19j"
        self.nominal_chips = 114

    def __repr__(self) -> str:
        return f"CGMinerS19j: {str(self.ip)}"
