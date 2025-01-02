from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M33SPlusVG20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M33SPlusVG20

    expected_chips = 112
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M33SPlusVG30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M33SPlusVG30

    expected_chips = 162
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M33SPlusVH20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M33SPlusVH20

    expected_chips = 100
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M33SPlusVH30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M33SPlusVH30

    expected_chips = None
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
