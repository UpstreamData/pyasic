from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M50SPlusVH30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusVH30

    expected_chips = 172
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusVH40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusVH40

    expected_chips = 180
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusVJ30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusVJ30

    expected_chips = 156
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusVJ40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusVJ40

    expected_chips = 164
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusVJ60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusVJ60

    expected_chips = 164
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusVK10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusVK10

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusVK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusVK20

    expected_chips = 117
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusVK30

    expected_chips = 123
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusVL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusVL10

    expected_chips = 82
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusVL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusVL20

    expected_chips = 86
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SPlusVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SPlusVL30

    expected_chips = 105
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
