from miners import BaseMiner


class S17e(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "S17e"
        self.nominal_chips = 135
        self.fan_count = 4
