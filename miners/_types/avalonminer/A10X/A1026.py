from miners import BaseMiner


class Avalon1026(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "Avalon 1026"
        self.nominal_chips = 80
        self.fan_count = 2
