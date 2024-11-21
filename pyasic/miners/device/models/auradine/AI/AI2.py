from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import AuradineMake


class AuradineAI2500(AuradineMake):
    raw_model = MinerModel.AURADINE.AI2500

    expected_fans = 0
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
