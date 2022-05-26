from miners import BaseMiner


class S19jPro(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "S19j Pro"
        self.nominal_chips = 126
        self.fan_count = 4
