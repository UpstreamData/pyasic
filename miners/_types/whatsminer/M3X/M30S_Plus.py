from miners import BaseMiner


class M30SPlus(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S+"
        self.nominal_chips = 156
        self.fan_count = 2


class M30SPlusVG60(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S+ VG60"
        self.nominal_chips = 86
        self.fan_count = 2


class M30SPlusVE40(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S+ VE40"
        self.nominal_chips = 156
        self.fan_count = 2


class M30SPlusVF20(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S+ VF20"
        self.nominal_chips = 111
        self.fan_count = 2
