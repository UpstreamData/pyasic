from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M66VK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66VK20

    expected_chips = 184
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66VK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66VK30

    expected_chips = 192
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66VL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66VL20

    expected_chips = 160
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66VL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66VL30

    expected_chips = 168
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
