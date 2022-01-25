from miners.bosminer import BOSMiner


class BOSMinerX17(BOSMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BOSMiner"
        self.nominal_chips = 65

    def __repr__(self) -> str:
        return f"BOSminerX17: {str(self.ip)}"
