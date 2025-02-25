from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M53SVH20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SVH20

    expected_chips = 198
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SVH30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SVH30

    expected_chips = 204
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SVJ30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SVJ30

    expected_chips = 180
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SVJ40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SVJ40

    expected_chips = 192
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SVK30

    expected_chips = 128
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
