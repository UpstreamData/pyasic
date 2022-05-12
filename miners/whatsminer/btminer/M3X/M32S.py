from miners.btminer import BTMiner


class BTMinerM32S(BTMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.nominal_chips = 78

    def __repr__(self) -> str:
        return f"M32S - BTMiner: {str(self.ip)}"
