from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M63SPlusPlusVL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SPlusPlusVL20

    expected_chips = 380
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
