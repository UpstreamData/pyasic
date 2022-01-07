from miners.cgminer import CGMiner


class CGMinerX17(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "CGMiner"

    def __repr__(self) -> str:
        return f"CGMinerX17: {str(self.ip)}"
