from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import X11HashRate
from .hashrate.unit import X11Unit


# make this json serializable
class _X11Algo(MinerAlgoType):
    hashrate = X11HashRate
    unit = X11Unit

    def __repr__(self):
        return "X11Algo"


X11Algo = _X11Algo("X11")
