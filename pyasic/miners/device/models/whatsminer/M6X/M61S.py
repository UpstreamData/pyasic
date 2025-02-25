from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M61SVL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61SVL10

    expected_chips = 164
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M61SVL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61SVL20

    expected_chips = 172
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M61SVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61SVL30

    expected_chips = 180
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
