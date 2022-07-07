from pyasic.miners import BaseMiner


class S19(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "S19"
        self.nominal_chips = 76
        self.fan_count = 4
