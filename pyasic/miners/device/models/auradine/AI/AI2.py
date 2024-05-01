from pyasic.device.models import MinerModels
from pyasic.miners.device.makes import AuradineMake


class AuradineAI2500(AuradineMake):
    raw_model = MinerModels.AURADINE.AI2500

    expected_fans = 0
