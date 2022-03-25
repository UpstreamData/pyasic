from miners.bosminer import BOSMiner


class BOSMinerX19(BOSMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BOSMiner"
        self.nominal_chips = 114

    def __repr__(self) -> str:
        return f"BOSminerX19: {str(self.ip)}"
