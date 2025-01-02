from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M36SVE10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M36SVE10

    expected_chips = 114
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
