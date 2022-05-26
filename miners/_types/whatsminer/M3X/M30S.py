from miners import BaseMiner


class M30S(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S"
        self.nominal_chips = 148
        self.fan_count = 2
