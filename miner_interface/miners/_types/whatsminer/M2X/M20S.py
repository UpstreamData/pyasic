from miner_interface.miners import BaseMiner


class M20S(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M20S"
        self.nominal_chips = 66
        self.fan_count = 2
