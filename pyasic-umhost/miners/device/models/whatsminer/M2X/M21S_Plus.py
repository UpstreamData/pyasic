from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M21SPlusV20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M21SPlusV20

    expected_chips = None
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
