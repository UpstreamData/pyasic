from miners.bmminer import BMMiner


class BMMinerT9(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "T9"
        self.api_type = "BMMiner"

    def __repr__(self) -> str:
        return f"BMMinerT9: {str(self.ip)}"
