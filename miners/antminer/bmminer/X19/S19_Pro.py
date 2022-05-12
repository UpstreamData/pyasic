from miners.bmminer import BMMiner


class BMMinerS19Pro(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BMMiner"
        self.model = "S19 Pro"
        self.nominal_chips = 114

    def __repr__(self) -> str:
        return f"BMMinerS19Pro: {str(self.ip)}"
