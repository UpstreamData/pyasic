from miner_interface.miners import BaseMiner


class M30S(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S"
        self.nominal_chips = 148
        self.fan_count = 2


class M30SV50(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S V50"
        self.nominal_chips = 156
        self.fan_count = 2


class M30SVG20(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S VG20"
        self.nominal_chips = 70
        self.fan_count = 2


class M30SVE20(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S VE20"
        self.nominal_chips = 111
        self.fan_count = 2


class M30SVE10(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S VE10"
        self.nominal_chips = 105
        self.fan_count = 2
