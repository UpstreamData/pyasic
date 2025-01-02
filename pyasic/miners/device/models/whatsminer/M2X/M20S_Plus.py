from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M20SPlusV30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M20SPlusV30

    expected_chips = None
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
