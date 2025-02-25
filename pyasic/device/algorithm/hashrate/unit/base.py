from enum import IntEnum


class AlgoHashRateUnitType(IntEnum):
    H: int
    KH: int
    MH: int
    GH: int
    TH: int
    PH: int
    EH: int
    ZH: int

    default: int

    def __str__(self):
        if self.value == self.H:
            return "H/s"
        if self.value == self.KH:
            return "KH/s"
        if self.value == self.MH:
            return "MH/s"
        if self.value == self.GH:
            return "GH/s"
        if self.value == self.TH:
            return "TH/s"
        if self.value == self.PH:
            return "PH/s"
        if self.value == self.EH:
            return "EH/s"
        if self.value == self.ZH:
            return "ZH/s"

    @classmethod
    def from_str(cls, value: str):
        if value == "H":
            return cls.H
        elif value == "KH":
            return cls.KH
        elif value == "MH":
            return cls.MH
        elif value == "GH":
            return cls.GH
        elif value == "TH":
            return cls.TH
        elif value == "PH":
            return cls.PH
        elif value == "EH":
            return cls.EH
        elif value == "ZH":
            return cls.ZH
        return cls.default

    def __repr__(self):
        return str(self)

    def model_dump(self):
        return {"value": self.value, "suffix": str(self)}


class GenericUnit(AlgoHashRateUnitType):
    H = 1
    KH = int(H) * 1000
    MH = int(KH) * 1000
    GH = int(MH) * 1000
    TH = int(GH) * 1000
    PH = int(TH) * 1000
    EH = int(PH) * 1000
    ZH = int(EH) * 1000

    default = H
