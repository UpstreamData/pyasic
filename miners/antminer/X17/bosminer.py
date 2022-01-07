from miners.bosminer import BOSminer


class BOSMinerX17(BOSminer):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BOSMiner"

    def __repr__(self) -> str:
        return f"BOSminerX17: {str(self.ip)}"
