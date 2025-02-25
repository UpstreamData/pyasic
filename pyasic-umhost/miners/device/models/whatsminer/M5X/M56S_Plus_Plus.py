from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M56SPlusPlusVK10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M56SPlusPlusVK10

    expected_chips = 160
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M56SPlusPlusVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M56SPlusPlusVK30

    expected_chips = 176
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M56SPlusPlusVK40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M56SPlusPlusVK40

    expected_chips = 132
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M56SPlusPlusVK50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M56SPlusPlusVK50

    expected_chips = 152
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
