from miners.bosminer import BOSMiner


class BOSMinerT19(BOSMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BOSMiner"
        self.model = "T19"
        self.nominal_chips = 114

    def __repr__(self) -> str:
        return f"BOSMinerT19: {str(self.ip)}"
