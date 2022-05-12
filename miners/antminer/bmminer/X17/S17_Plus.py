from miners.bmminer import BMMiner


class BMMinerS17Plus(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BMMiner"
        self.model = "S17+"
        self.nominal_chips = 65

    def __repr__(self) -> str:
        return f"BMMinerS17+: {str(self.ip)}"
