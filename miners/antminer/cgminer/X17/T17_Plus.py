from miners.cgminer import CGMiner


class CGMinerT17Plus(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "CGMiner"
        self.model = "T17+"
        self.nominal_chips = 65

    def __repr__(self) -> str:
        return f"CGMinerT17+: {str(self.ip)}"
