from miners import BaseMiner


class M31SPlus(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S+"
        self.nominal_chips = 78
