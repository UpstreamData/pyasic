from pyasic.miners import BaseMiner


class Avalon1066(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "Avalon 1066"
        self.nominal_chips = 114
        self.fan_count = 4
