from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M30V10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30V10

    expected_chips = 105
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M30V20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30V20

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
