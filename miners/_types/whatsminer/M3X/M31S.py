from miners import BaseMiner


class M31S(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M31S"
