from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M53VH30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53VH30

    expected_chips = 128
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53VH40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53VH40

    expected_chips = 174
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53VH50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53VH50

    expected_chips = 162
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53VK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53VK30

    expected_chips = 100
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53VK60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53VK60

    expected_chips = 100
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
