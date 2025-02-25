from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M64VL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M64VL30

    expected_chips = 114
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M64VL40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M64VL40

    expected_chips = 120
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
