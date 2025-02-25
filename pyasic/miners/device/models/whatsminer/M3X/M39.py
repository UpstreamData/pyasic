from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M39V10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M39V10

    expected_chips = 50
    expected_fans = 0
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M39V20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M39V20

    expected_chips = 54
    expected_fans = 0
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M39V30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M39V30

    expected_chips = 68
    expected_fans = 0
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
