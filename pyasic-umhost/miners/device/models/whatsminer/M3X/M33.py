from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M33V10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M33V10

    expected_chips = 33
    expected_fans = 0
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M33V20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M33V20

    expected_chips = 62
    expected_fans = 0
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M33V30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M33V30

    expected_chips = 66
    expected_fans = 0
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
