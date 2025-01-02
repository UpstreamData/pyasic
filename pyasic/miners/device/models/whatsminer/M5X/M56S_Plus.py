from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M56SPlusVJ30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M56SPlusVJ30

    expected_chips = 176
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M56SPlusVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M56SPlusVK30

    expected_chips = 108
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M56SPlusVK40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M56SPlusVK40

    expected_chips = 114
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M56SPlusVK50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M56SPlusVK50

    expected_chips = 120
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
