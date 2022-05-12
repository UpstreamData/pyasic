from miners.btminer import BTMiner


class BTMinerM20S(BTMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.nominal_chips = 66

    def __repr__(self) -> str:
        return f"M20S - BTMiner: {str(self.ip)}"
