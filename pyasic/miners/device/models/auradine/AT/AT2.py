from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import AuradineMake


class AuradineAT2860(AuradineMake):
    raw_model = MinerModel.AURADINE.AT2860

    expected_fans = 4
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class AuradineAT2880(AuradineMake):
    raw_model = MinerModel.AURADINE.AT2880

    expected_fans = 4
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
