from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M34SPlusVE10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M34SPlusVE10

    expected_chips = 116
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
