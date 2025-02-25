from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M33SPlusPlusVG40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M33SPlusPlusVG40

    expected_chips = 174
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M33SPlusPlusVH20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M33SPlusPlusVH20

    expected_chips = 112
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M33SPlusPlusVH30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M33SPlusPlusVH30

    expected_chips = None
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
