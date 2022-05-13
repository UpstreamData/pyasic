from miners import BaseMiner


class M21SPlus(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M21S+"
        self.nominal_chips = 105
