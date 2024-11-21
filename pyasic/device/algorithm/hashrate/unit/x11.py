from __future__ import annotations

from .base import AlgoHashRateUnitType


class X11Unit(AlgoHashRateUnitType):
    H = 1
    KH = int(H) * 1000
    MH = int(KH) * 1000
    GH = int(MH) * 1000
    TH = int(GH) * 1000
    PH = int(TH) * 1000
    EH = int(PH) * 1000
    ZH = int(EH) * 1000

    default = GH
