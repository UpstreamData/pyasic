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

    @classmethod
    def from_str(cls, value):
        return cls.default
