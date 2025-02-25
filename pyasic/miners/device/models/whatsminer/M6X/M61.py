from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M61VK10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61VK10

    expected_chips = 180
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M61VK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61VK20

    expected_chips = 184
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M61VK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61VK30

    expected_chips = 188
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M61VK40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61VK40

    expected_chips = 192
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M61VL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61VL10

    expected_chips = 135
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M61VL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61VL30

    expected_chips = 141
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M61VL40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61VL40

    expected_chips = 144
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M61VL50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61VL50

    expected_chips = 147
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M61VL60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M61VL60

    expected_chips = 150
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
