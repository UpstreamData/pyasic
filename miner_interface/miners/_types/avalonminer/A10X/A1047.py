from miner_interface.miners import BaseMiner


class Avalon1047(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "Avalon 1047"
        self.nominal_chips = 80
        self.fan_count = 2
