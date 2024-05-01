from pyasic.device.models import MinerModels
from pyasic.miners.device.makes import AuradineMake


class AuradineAD2500(AuradineMake):
    raw_model = MinerModels.AURADINE.AD2500

    expected_fans = 0
