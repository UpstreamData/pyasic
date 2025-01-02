from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M50SPlusPlusVK10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusPlusVK10

    expected_chips = 117
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusPlusVK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusPlusVK20

    expected_chips = 123
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusPlusVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusPlusVK30

    expected_chips = 156
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusPlusVK40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusPlusVK40

    expected_chips = 129
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusPlusVK50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusPlusVK50

    expected_chips = 135
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusPlusVK60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusPlusVK60

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusPlusVL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusPlusVL20

    expected_chips = 86
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusPlusVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusPlusVL30

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusPlusVL40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusPlusVL40

    expected_chips = 117
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusPlusVL50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusPlusVL50

    expected_chips = 105
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusPlusVL60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusPlusVL60

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
