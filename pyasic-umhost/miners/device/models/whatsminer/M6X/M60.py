from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M60VK10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60VK10

    expected_chips = 164
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60VK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60VK20

    expected_chips = 172
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60VK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60VK30

    expected_chips = 215
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60VK40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60VK40

    expected_chips = 180
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60VK6A(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60VK6A

    expected_chips = 172
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60VL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60VL10

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60VL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60VL20

    expected_chips = 117
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60VL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60VL30

    expected_chips = 123
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60VL40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60VL40

    expected_chips = 129
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60VL50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60VL50

    expected_chips = 135
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
