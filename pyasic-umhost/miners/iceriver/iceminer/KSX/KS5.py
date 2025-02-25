from pyasic.miners.backends.iceriver import IceRiver
from pyasic.miners.device.models.iceriver import KS5, KS5L, KS5M


class IceRiverKS5(IceRiver, KS5):
    pass


class IceRiverKS5L(IceRiver, KS5L):
    pass


class IceRiverKS5M(IceRiver, KS5M):
    pass
