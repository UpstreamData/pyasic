from __future__ import annotations

from enum import IntEnum

from .base import MinerAlgoType


class EquihashUnit(IntEnum):
    H = 1
    KH = int(H) * 1000
    MH = int(KH) * 1000
    GH = int(MH) * 1000
    TH = int(GH) * 1000
    PH = int(TH) * 1000
    EH = int(PH) * 1000
    ZH = int(EH) * 1000

    default = KH

    def __str__(self):
        if self.value == self.H:
            return "Sol/s"
        if self.value == self.KH:
            return "KSol/s"
        if self.value == self.MH:
            return "MSol/s"
        if self.value == self.GH:
            return "GSol/s"
        if self.value == self.TH:
            return "TSol/s"
        if self.value == self.PH:
            return "PSol/s"
        if self.value == self.EH:
            return "ESol/s"
        if self.value == self.ZH:
            return "ZSol/s"

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


# make this json serializable
class _EquihashAlgo(MinerAlgoType):
    unit = EquihashUnit

    def __repr__(self):
        return "EquihashAlgo"


EquihashAlgo = _EquihashAlgo("Equihash")
