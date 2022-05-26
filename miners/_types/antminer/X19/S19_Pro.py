from miners import BaseMiner


class S19Pro(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "S19 Pro"
        self.nominal_chips = 114
        self.fan_count = 4
