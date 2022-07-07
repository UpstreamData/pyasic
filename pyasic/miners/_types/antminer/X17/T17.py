from pyasic.miners import BaseMiner


class T17(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "T17"
        self.nominal_chips = 30
        self.fan_count = 4
