from miners.bosminer import BOSminer


class BOSMinerS9(BOSminer):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "S9"
        self.api_type = "BOSMiner"

    def __repr__(self) -> str:
        return f"BOSminerS9: {str(self.ip)}"
