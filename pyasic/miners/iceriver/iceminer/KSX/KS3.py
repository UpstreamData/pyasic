from pyasic.miners.backends.iceriver import IceRiver
from pyasic.miners.device.models.iceriver import KS3, KS3L, KS3M


class IceRiverKS3(IceRiver, KS3):
    pass


class IceRiverKS3L(IceRiver, KS3L):
    pass


class IceRiverKS3M(IceRiver, KS3M):
    pass
