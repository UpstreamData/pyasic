from pyasic.miners import BaseMiner


class T9(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "T9"
        self.nominal_chips = 57
        self.fan_count = 2
