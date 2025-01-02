from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M21V10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M21V10

    expected_chips = 33
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
