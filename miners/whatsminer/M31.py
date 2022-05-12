from miners.btminer import BTMiner


class BTMinerM31(BTMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.nominal_chips = 78

    def __repr__(self) -> str:
        return f"M31 - BTMiner: {str(self.ip)}"
