from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M63SVK10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SVK10

    expected_chips = 340
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63SVK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SVK20

    expected_chips = 350
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63SVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SVK30

    expected_chips = 370
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63SVK60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SVK60

    expected_chips = 350
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63SVL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SVL10

    expected_chips = 228
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63SVL50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SVL50

    expected_chips = 288
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M63SVL60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M63SVL60

    expected_chips = 288
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
