from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M66SPlusPlusVL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SPlusPlusVL20

    expected_chips = 368
    expected_fans = 0
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
