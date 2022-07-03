from miner_interface.miners import BaseMiner


class S9(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "S9"
        self.nominal_chips = 63
        self.fan_count = 2
