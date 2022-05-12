from miners.bmminer import BMMiner


class BMMinerT17e(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api_type = "BMMiner"
        self.model = "T17e"
        self.nominal_chips = 65

    def __repr__(self) -> str:
        return f"BMMinerT17e: {str(self.ip)}"
