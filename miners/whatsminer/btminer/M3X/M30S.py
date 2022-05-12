from miners.btminer import BTMiner


class BTMinerM30S(BTMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)

    def __repr__(self) -> str:
        return f"M30S - BTMiner: {str(self.ip)}"
