from miners import BaseMiner


class S17(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "S17"
        self.nominal_chips = 48
