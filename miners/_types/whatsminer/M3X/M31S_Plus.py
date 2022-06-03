from miners import BaseMiner


class M31SPlus(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+"
        self.nominal_chips = 78
        self.fan_count = 2


class M31SPlusVE20(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+VE20"
        self.nominal_chips = 78
        self.fan_count = 2
