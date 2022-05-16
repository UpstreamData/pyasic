from miners import BaseMiner


class T17Plus(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "T17+"
        self.nominal_chips = 44
