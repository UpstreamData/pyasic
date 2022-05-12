from miners.cgminer import CGMiner


class CGMinerT19(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "CGMiner"
        self.model = "T19"
        self.nominal_chips = 114

    def __repr__(self) -> str:
        return f"CGMinerT19: {str(self.ip)}"
