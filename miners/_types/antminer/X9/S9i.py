from miners import BaseMiner


class S9i(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "S9i"
        self.nominal_chips = 63
