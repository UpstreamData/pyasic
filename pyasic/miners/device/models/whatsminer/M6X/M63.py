from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M63VK10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63VK10

    expected_chips = None
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63VK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63VK20

    expected_chips = 264
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63VK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63VK30

    expected_chips = 272
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63VL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63VL10

    expected_chips = 174
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63VL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63VL30

    expected_chips = 216
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
