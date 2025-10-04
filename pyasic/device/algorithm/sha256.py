from __future__ import annotations

from .base import MinerAlgoType
from .hashrate.sha256 import SHA256HashRate
from .hashrate.unit.sha256 import SHA256Unit

__all__ = ["SHA256Algo", "SHA256HashRate", "SHA256Unit"]


# make this json serializable
class SHA256Algo(MinerAlgoType):
    hashrate: type[SHA256HashRate] = SHA256HashRate
    unit: type[SHA256Unit] = SHA256Unit

    name = "SHA256"
