from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M54SPlusPlusVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M54SPlusPlusVK30

    expected_chips = 96
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M54SPlusPlusVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M54SPlusPlusVL30

    expected_chips = 68
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M54SPlusPlusVL40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M54SPlusPlusVL40

    expected_chips = 90
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
