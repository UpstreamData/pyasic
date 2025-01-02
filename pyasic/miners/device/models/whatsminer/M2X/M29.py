from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M29V10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M29V10

    expected_chips = 50
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
