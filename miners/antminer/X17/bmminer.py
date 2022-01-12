from miners.bmminer import BMMiner


class BMMinerX17(BMMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)

    def __repr__(self) -> str:
        return f"BMMinerX17: {str(self.ip)}"
