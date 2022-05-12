from miners.btminer import BTMiner


class BTMinerM21S(BTMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.nominal_chips = 105

    def __repr__(self) -> str:
        return f"M21S - BTMiner: {str(self.ip)}"
