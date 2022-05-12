from miners.bmminer import BMMiner


class BMMinerS9(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "S9"
        self.api_type = "BMMiner"

    def __repr__(self) -> str:
        return f"BMMinerS9: {str(self.ip)}"
