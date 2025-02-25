from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M53SPlusVJ30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SPlusVJ30

    expected_chips = 240
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SPlusVJ40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SPlusVJ40

    expected_chips = 248
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SPlusVJ50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SPlusVJ50

    expected_chips = 264
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SPlusVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SPlusVK30

    expected_chips = 168
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
