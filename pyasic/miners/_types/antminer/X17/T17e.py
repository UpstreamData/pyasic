from pyasic.miners import BaseMiner


class T17e(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "T17e"
        self.nominal_chips = 78
        self.fan_count = 4
