from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M66SPlusVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SPlusVK30

    expected_chips = 440
    expected_fans = 0
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M66SPlusVL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SPlusVL10

    expected_chips = 220
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66SPlusVL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SPlusVL20

    expected_chips = 230
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66SPlusVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SPlusVL30

    expected_chips = 240
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66SPlusVL40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SPlusVL40

    expected_chips = 250
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66SPlusVL60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SPlusVL60

    expected_chips = 200
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
