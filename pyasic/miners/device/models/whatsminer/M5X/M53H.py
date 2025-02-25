from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M53HVH10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53HVH10

    expected_chips = 56
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
