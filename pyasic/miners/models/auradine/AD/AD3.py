from pyasic.device.models import MinerModels
from pyasic.miners.device.makes import AuradineMake


class AuradineAD3500(AuradineMake):
    raw_model = MinerModels.AURADINE.AD3500

    expected_fans = 0
