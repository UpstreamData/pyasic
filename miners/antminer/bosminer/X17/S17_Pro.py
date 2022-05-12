from miners.bosminer import BOSMiner


class BOSMinerS17Pro(BOSMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BOSMiner"
        self.model = "S17 Pro"
        self.nominal_chips = 65

    def __repr__(self) -> str:
        return f"BOSMinerS17Pro: {str(self.ip)}"
