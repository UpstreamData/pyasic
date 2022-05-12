from miners.cgminer import CGMiner


class CGMinerT17e(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "CGMiner"
        self.model = "T17e"
        self.nominal_chips = 65

    def __repr__(self) -> str:
        return f"CGMinerT17e: {str(self.ip)}"
