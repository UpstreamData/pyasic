from pyasic.miners import BaseMiner


class M32S(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M32S"
        self.nominal_chips = 78
        self.fan_count = 2
