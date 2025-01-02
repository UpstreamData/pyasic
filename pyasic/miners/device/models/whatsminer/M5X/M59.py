from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M59VH30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M59VH30

    expected_chips = 132
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
