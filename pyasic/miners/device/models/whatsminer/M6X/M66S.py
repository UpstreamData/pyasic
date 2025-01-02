from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M66SVK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SVK20

    expected_chips = 368
    expected_fans = 0
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M66SVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SVK30

    expected_chips = 384
    expected_fans = 0
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M66SVK40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SVK40

    expected_chips = 240
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66SVK50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SVK50

    expected_chips = 250
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66SVK60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SVK60

    expected_chips = 250
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66SVL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SVL10

    expected_chips = 168
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66SVL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SVL20

    expected_chips = 176
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66SVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SVL30

    expected_chips = 192
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66SVL40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SVL40

    expected_chips = 200
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M66SVL50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M66SVL50

    expected_chips = 210
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
