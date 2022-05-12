from miners.bosminer import BOSMiner


class BOSMinerT17Plus(BOSMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BOSMiner"
        self.model = "T17+"
        self.nominal_chips = 65

    def __repr__(self) -> str:
        return f"BOSMinerT17+: {str(self.ip)}"
