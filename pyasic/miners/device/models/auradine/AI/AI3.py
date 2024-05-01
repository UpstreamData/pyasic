from pyasic.device.models import MinerModels
from pyasic.miners.device.makes import AuradineMake


class AuradineAI3680(AuradineMake):
    raw_model = MinerModels.AURADINE.AI3680

    expected_fans = 0
