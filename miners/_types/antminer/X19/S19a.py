from miners import BaseMiner


class S19a(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "S19a"
        self.nominal_chips = 72
