from miners import BaseMiner


class M30SPlusPlusVG30(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S++V30"
        self.nominal_chips = 111
        self.fan_count = 2


class M30SPlusPlusVG40(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S++V40"
        self.nominal_chips = 117
        self.fan_count = 2
