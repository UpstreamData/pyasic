from pyasic.device.models import MinerModels
from pyasic.miners.device.makes import AuradineMake


class AuradineAT2860(AuradineMake):
    raw_model = MinerModels.AURADINE.AT2860

    expected_fans = 4


class AuradineAT2880(AuradineMake):
    raw_model = MinerModels.AURADINE.AT2880

    expected_fans = 4
