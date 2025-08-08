from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import BraiinsMake


class BMM100(BraiinsMake):
    raw_model = MinerModel.BRAIINS.BMM100

    expected_chips = 1
    expected_hashboards = 1
    expected_fans = 1
    algo = MinerAlgo.SHA256


class BMM101(BraiinsMake):
    raw_model = MinerModel.BRAIINS.BMM101

    expected_chips = 1
    expected_hashboards = 1
    expected_fans = 1
    algo = MinerAlgo.SHA256
