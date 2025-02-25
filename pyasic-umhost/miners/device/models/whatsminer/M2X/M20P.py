from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M20PV10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M20PV10

    expected_chips = 156
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M20PV30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M20PV30

    expected_chips = 148
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
