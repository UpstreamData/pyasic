from __future__ import annotations

from .base import MinerAlgoType
from .hashrate import X11HashRate
from .hashrate.unit import X11Unit


# make this json serializable
class X11Algo(MinerAlgoType):
    hashrate: type[X11HashRate] = X11HashRate
    unit: type[X11Unit] = X11Unit

    name = "X11"
