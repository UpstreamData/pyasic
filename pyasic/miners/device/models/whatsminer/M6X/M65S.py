from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M65SVK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M65SVK20

    expected_chips = 350
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M65SVL60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M65SVL60

    expected_chips = 288
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
