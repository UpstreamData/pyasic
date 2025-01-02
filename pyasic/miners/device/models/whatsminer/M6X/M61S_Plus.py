from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M61SPlusVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61SPlusVL30

    expected_chips = 225
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
