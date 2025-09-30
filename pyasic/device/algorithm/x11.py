from __future__ import annotations

from .base import MinerAlgoType
from .hashrate.unit.x11 import X11Unit
from .hashrate.x11 import X11HashRate

__all__ = ["X11Algo", "X11HashRate", "X11Unit"]


# make this json serializable
class X11Algo(MinerAlgoType):
    hashrate: type[X11HashRate] = X11HashRate
    unit: type[X11Unit] = X11Unit

    name = "X11"
