from miners import BaseMiner


class M21SV60(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M21S V60"
        self.nominal_chips = 105
        self.fan_count = 2


class M21SV20(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M21S V20"
        self.nominal_chips = 66
        self.fan_count = 2
