from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M63SPlusVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SPlusVK30

    expected_chips = 456
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63SPlusVL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SPlusVL10

    expected_chips = 304
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63SPlusVL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SPlusVL20

    expected_chips = 340
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63SPlusVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SPlusVL30

    expected_chips = 370
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63SPlusVL50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SPlusVL50

    expected_chips = 272
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
