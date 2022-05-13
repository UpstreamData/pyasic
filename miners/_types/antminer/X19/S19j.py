from miners import BaseMiner


class S19j(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "S19j"
        self.nominal_chips = 114
