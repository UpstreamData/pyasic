from miners import BaseMiner


class M30SPlusPlus(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "M30S++"
        self.nominal_chips = 117


# TODO: handle different chip counts, 111, 117,(128)
