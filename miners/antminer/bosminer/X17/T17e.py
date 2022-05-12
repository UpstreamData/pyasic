from miners.bosminer import BOSMiner


class BOSMinerT17e(BOSMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BOSMiner"
        self.model = "T17e"
        self.nominal_chips = 65

    def __repr__(self) -> str:
        return f"BOSMinerT17e: {str(self.ip)}"
