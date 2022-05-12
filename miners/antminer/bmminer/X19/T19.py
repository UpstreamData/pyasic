from miners.bmminer import BMMiner


class BMMinerT19(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BMMiner"
        self.model = "T19"
        self.nominal_chips = 114

    def __repr__(self) -> str:
        return f"BMMinerT19: {str(self.ip)}"
