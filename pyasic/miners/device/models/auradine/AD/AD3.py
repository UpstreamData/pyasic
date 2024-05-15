from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import AuradineMake


class AuradineAD3500(AuradineMake):
    raw_model = MinerModel.AURADINE.AD3500

    expected_fans = 0
