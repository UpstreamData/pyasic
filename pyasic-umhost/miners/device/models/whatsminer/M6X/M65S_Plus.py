from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M65SPlusVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M65SPlusVK30

    expected_chips = 456
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
