from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M56SVH30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M56SVH30

    expected_chips = 152
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M56SVJ30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M56SVJ30

    expected_chips = 132
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M56SVJ40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M56SVJ40

    expected_chips = 152
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
