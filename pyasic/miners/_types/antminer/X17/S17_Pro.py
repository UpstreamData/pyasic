from pyasic.miners import BaseMiner


class S17Pro(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "S17 Pro"
        self.nominal_chips = 48
        self.fan_count = 4
