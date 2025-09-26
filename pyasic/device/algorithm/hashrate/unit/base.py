from enum import IntEnum


class AlgoHashRateUnitType(IntEnum):
    def __str__(self):
        if hasattr(self.__class__, "H") and self.value == self.__class__.H:
            return "H/s"
        if hasattr(self.__class__, "KH") and self.value == self.__class__.KH:
            return "KH/s"
        if hasattr(self.__class__, "MH") and self.value == self.__class__.MH:
            return "MH/s"
        if hasattr(self.__class__, "GH") and self.value == self.__class__.GH:
            return "GH/s"
        if hasattr(self.__class__, "TH") and self.value == self.__class__.TH:
            return "TH/s"
        if hasattr(self.__class__, "PH") and self.value == self.__class__.PH:
            return "PH/s"
        if hasattr(self.__class__, "EH") and self.value == self.__class__.EH:
            return "EH/s"
        if hasattr(self.__class__, "ZH") and self.value == self.__class__.ZH:
            return "ZH/s"
        return ""

    @classmethod
    def from_str(cls, value: str):
        if value == "H" and hasattr(cls, "H"):
            return cls.H
        elif value == "KH" and hasattr(cls, "KH"):
            return cls.KH
        elif value == "MH" and hasattr(cls, "MH"):
            return cls.MH
        elif value == "GH" and hasattr(cls, "GH"):
            return cls.GH
        elif value == "TH" and hasattr(cls, "TH"):
            return cls.TH
        elif value == "PH" and hasattr(cls, "PH"):
            return cls.PH
        elif value == "EH" and hasattr(cls, "EH"):
            return cls.EH
        elif value == "ZH" and hasattr(cls, "ZH"):
            return cls.ZH
        if hasattr(cls, "default"):
            return cls.default
        return None

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
