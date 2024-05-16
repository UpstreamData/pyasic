from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import AuradineMake


class AuradineAI3680(AuradineMake):
    raw_model = MinerModel.AURADINE.AI3680

    expected_fans = 0
