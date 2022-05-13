from miners._backends.cgminer import CGMiner


class CGMinerT9(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "T9"
        self.api_type = "CGMiner"

    def __repr__(self) -> str:
        return f"CGMinerT9: {str(self.ip)}"
