from miners.bosminer import BOSMiner


class BOSMinerS19jPro(BOSMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BOSMiner"
        self.model = "S19j Pro"
        self.nominal_chips = 114

    def __repr__(self) -> str:
        return f"BOSMinerS19jPro: {str(self.ip)}"
